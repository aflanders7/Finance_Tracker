from flask import Flask, render_template, json, redirect, request, jsonify
import os
from flask_mysqldb import MySQL
from database.db_connector import connect_to_database, execute_query
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import requests

load_dotenv(find_dotenv())

host = os.environ.get("host")
user = os.environ.get("user")
passwd = os.environ.get("passwd")
db = os.environ.get("db")

# Configuration

app = Flask(__name__)

app.config['MYSQL_HOST'] = host
app.config['MYSQL_USER'] = user
app.config['MYSQL_PASSWORD'] = passwd
app.config['MYSQL_DB'] = db
mysql = MySQL(app)


def get_data(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    return data

def get_data_values(query, values):
    cur = mysql.connection.cursor()
    cur.execute(query, values)
    data = cur.fetchall()
    return data

def commit_data_values(query, values):
    cur = mysql.connection.cursor()
    cur.execute(query, values)
    mysql.connection.commit()


# Routes 

@app.route('/')
def root():
    return redirect("/expenses")

# route for FAQ page
@app.route('/faq')
def faq():
    return render_template("faq.html")


# route for expenses page
@app.route('/expenses', methods=["POST", "GET"])
def expense():
    if request.method == "GET":
        query = "SELECT * FROM Expenses ORDER BY Day DESC;"
        data = get_data(query)

        query2 = 'SELECT SUM(Amount) FROM Expenses'
        total = get_data(query2)
        
        return render_template("expenses.j2", Expenses=data, total=total)

    if request.method == "POST":

        if request.form.get("Add_Expense"):
            Name = request.form["name"]
            Amount = request.form["amount"]
            Category = request.form["category"]
            Description = request.form["description"]
            Day = request.form["date"]
        
            if Description == "":
                query = "INSERT INTO Expenses (Name, Amount, Category, Day) VALUES (%s, %s, %s, %s);"
                commit_data_values(query, (Name, Amount, Category, Day))

            else:
                query = "INSERT INTO Expenses (Name, Amount, Category, Description, Day) VALUES (%s, %s, %s, %s, %s);"
                commit_data_values(query, (Name, Amount, Category, Description, Day))
            
            return redirect("/expenses")

# routes for sorting on expenses page

@app.route('/expenses-cost', methods=["GET"])
def expense2():
    if request.method == "GET":
        query = "SELECT * FROM Expenses ORDER BY Amount;"
        data = get_data(query)

        query2 = 'SELECT SUM(Amount) FROM Expenses'
        total = get_data(query2)
        
        return render_template("expenses.j2", Expenses=data, total=total)

@app.route('/expenses-category', methods=["GET"])
def expense3():
    if request.method == "GET":
        query = "SELECT * FROM Expenses ORDER BY Category;"
        data = get_data(query)

        query2 = 'SELECT SUM(Amount) FROM Expenses'
        total = get_data(query2)
        
        return render_template("expenses.j2", Expenses=data, total=total)


# route for search function on expenses page

@app.route('/expenses-search', methods=["POST"])
def expense4():
    if request.method == "POST":
        Name = request.form["searchName"]
        # return to full chart if the reset button is selected
        if Name == "":
            return redirect("/expenses")

        query = "SELECT * FROM Expenses WHERE Name LIKE "'%s'";"
        data = get_data_values(query, (Name,))

        query2 = "SELECT SUM(Amount) FROM Expenses WHERE Name LIKE "'%s'";"
        total = get_data_values(query2, (Name,))
        
        return render_template("expenses.j2", Expenses=data, total=total)

# routes for deletion on expenses page table

@app.route('/delete_expense/<int:id>')
def delete_expense(id):
    query = "DELETE FROM Expenses where ID = '%s';"
    commit_data_values(query, (id,))
    return redirect("/expenses")


# routes for graph page

@app.route('/graph', methods=["GET"])
def graph():
    if request.method == "GET":

        query = 'SELECT SUM(Amount), MONTH(Day), YEAR(Day) FROM Expenses GROUP BY YEAR(Day), MONTH(DAY);'
        data = get_data(query)

        money, dates, years = zip(*data)
        MONTHS = ['January','February','March','April','May','June','July','August','September','October',
            'November','December']

        month = []
        for index in range(len(dates)):
            month_val = dates[index] - 1
            month.append(MONTHS[month_val] + " " + str(years[index]))
        
        query2 = 'SELECT SUM(Amount) FROM Expenses'
        total = get_data(query2)

        categories = microservice()
        labels2 = list(categories.keys())
        data2 = list(categories.values())

        return  render_template("graph.html", labels=month, data=money, total=total, labels2=labels2, data2=data2)


# microservice setup

url = "http://127.0.0.1:3008/" #microservice url

@app.route("/check", methods=['GET'])
def microservice():
    query = 'SELECT SUM(Amount), Category FROM Expenses GROUP BY Category;'
    data = get_data(query)
    mylist = data
    result = call_the_microservice(mylist)
    return result


def call_the_microservice(list):  
    response = requests.get(url, params={'catlist': list})
    percent = response.json().get("result")
    return percent


# Listener

if __name__ == "__main__":
	app.run(port=5008)