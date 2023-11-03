from flask import Flask, render_template, json, redirect, request, jsonify
import os
from flask_mysqldb import MySQL
from database.db_connector import connect_to_database, execute_query
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
#import requests

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
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        print(data)

        query3 = 'SELECT SUM(Amount) FROM Expenses'
        cur = mysql.connection.cursor()
        cur.execute(query3)
        total = cur.fetchall()
        print(total)
        
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
                cur = mysql.connection.cursor()
                cur.execute(query, (Name, Amount, Category, Day))
                mysql.connection.commit()

            else:
                query = "INSERT INTO Expenses (Name, Amount, Category, Description, Day) VALUES (%s, %s, %s, %s, %s);"
                cur = mysql.connection.cursor()
                cur.execute(query, (Name, Amount, Category, Description, Day))
                mysql.connection.commit()
            
            return redirect("/expenses")

# routes for sorting on expenses page

@app.route('/expenses-cost', methods=["GET"])
def expense2():
    if request.method == "GET":
        query = "SELECT * FROM Expenses ORDER BY Amount;"
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        print(data)

        query3 = 'SELECT SUM(Amount) FROM Expenses'
        cur = mysql.connection.cursor()
        cur.execute(query3)
        total = cur.fetchall()
        print(total)
        
        return render_template("expenses.j2", Expenses=data, total=total)

@app.route('/expenses-category', methods=["GET"])
def expense3():
    if request.method == "GET":
        query = "SELECT * FROM Expenses ORDER BY Category;"
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        print(data)

        query3 = 'SELECT SUM(Amount) FROM Expenses'
        cur = mysql.connection.cursor()
        cur.execute(query3)
        total = cur.fetchall()
        print(total)
        
        return render_template("expenses.j2", Expenses=data, total=total)


# route for search function on expenses page

@app.route('/expenses-search', methods=["POST"])
def expense4():
    if request.method == "POST":
        Name = request.form["searchName"]
        # return to full chart if the reset button is selected
        if Name == "":
            return redirect("/expenses")
        print(Name)
        query = "SELECT * FROM Expenses WHERE Name LIKE "'%s'";"
        cur = mysql.connection.cursor()
        cur.execute(query,(Name,))
        data = cur.fetchall()
        print(data)

        query3 = "SELECT SUM(Amount) FROM Expenses WHERE Name LIKE "'%s'";"
        cur = mysql.connection.cursor()
        cur.execute(query3,(Name,))
        total = cur.fetchall()
        print(total)
        
        return render_template("expenses.j2", Expenses=data, total=total)

# routes for deletion on expenses page table

@app.route('/delete_expense/<int:id>')
def delete_expense(id):
    query = "DELETE FROM Expenses where ID = '%s';"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()
    return redirect("/expenses")


# routes for graph page

@app.route('/graph', methods=["GET"])
def graph():
    if request.method == "GET":

        query = 'SELECT SUM(Amount), MONTH(Day), YEAR(Day) FROM Expenses GROUP BY YEAR(Day), MONTH(DAY);'
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        print(data)

        money, dates, years = zip(*data)
        print(years)
        print(dates)
        month = []
        MONTHS = ['January','February','March','April','May','June','July','August','September','October',
            'November','December']

        for data_month in dates:
            month.append(MONTHS[data_month-1]) #+ str(years[data_month]))
        
        for month_index in range(len(month)):
            month[month_index] = month[month_index] + " " + str((years[month_index]))


        #query2 = 'SELECT SUM(Amount), Category FROM Expenses GROUP BY Category;'
        #cur = mysql.connection.cursor()
        #cur.execute(query2)
        #dat = cur.fetchall()

        query3 = 'SELECT SUM(Amount) FROM Expenses'
        cur = mysql.connection.cursor()
        cur.execute(query3)
        total = cur.fetchall()
        print(total)

        return  render_template("graph.html", labels=month, data=money, total=total)


# microservice setup

url = "http://127.0.0.1:8010/" #microservice url


def call_microservie():

    query2 = 'SELECT SUM(Amount), Category FROM Expenses GROUP BY Category;'
    cur = mysql.connection.cursor()
    cur.execute(query2)
    dat = cur.fetchall()
    mylist = dat
    response = requests.get(url, params={'catlist': mylist})
    return response.json().get("result")


@app.route("/check", methods=['GET'])
def check_micro():
	result = call_microservie()

	return jsonify({"result": result})

# Listener

if __name__ == "__main__":
	app.run(port=5008)