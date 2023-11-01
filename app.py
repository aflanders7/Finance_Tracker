from flask import Flask, render_template, json, redirect, request
import os
from flask_mysqldb import MySQL
from database.db_connector import connect_to_database, execute_query
from dotenv import load_dotenv, find_dotenv
from datetime import datetime

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

@app.route('/expenses', methods=["POST", "GET"])
def expense():
    if request.method == "GET":
        query = "SELECT * FROM Expenses;"
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        print(data)
        return render_template("expenses.j2", Expenses=data)

    if request.method == "POST":
        Name = request.form["name"]
        Amount = request.form["amount"]
        Category = request.form["category"]
        Description = request.form["description"]
        Day = request.form["date"]

        if request.form.get("Add_Expense"):
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

@app.route('/delete_expense/<int:id>')
def delete_expense(id):
    query = "DELETE FROM Expenses where ID = '%s';"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()
    return redirect("/expenses")

# User functions
@app.route('/graph', methods=["GET"])
def graph():
    if request.method == "GET":
        #Date2 = DateTime.Now.ToString("yyyy-MM-dd")
        #Date1 = (datetime.datetime.now() - datetime.timedelta(30)).ToString("yyyy-MM-dd")
        Date1 = '2023-10-01'
        Date2 = '2023-11-05'
        #query = "SELECT SUM(Amount), CAST(Day as DATE) FROM Expenses GROUP BY Day;"
        query = 'SELECT SUM(Amount), MONTH(Day) FROM Expenses GROUP BY MONTH(Day);'
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        print(data)

        money, dates = zip(*data)
        month = []
        MONTHS = ['January','February','March','April','May','June','July','August','September','October',
            'November','December']

        for mon in dates:
            month.append(MONTHS[mon])

        print(month)

        return  render_template("graph.html", labels=month, data=money)

    #Date1 = request.form["date1"]
    #Date2 = request.form["date2"]


# Listener

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5008))
    app.run(port=port, debug=True)