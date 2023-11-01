from flask import Flask, render_template, json, redirect, request
import os
from flask_mysqldb import MySQL
from database.db_connector import connect_to_database, execute_query
from dotenv import load_dotenv, find_dotenv

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
        query = "SELECT Name, Amount, Category, Description, Day FROM Expenses;"
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        return render_template("expenses.j2", Expenses=data)

    if request.method == "POST":
        if request.form.get("Add_Expense"):
            Name = request.form["name"]
            Amount = request.form["amount"]
            Category = request.form["category"]
            Description = request.form["description"]
            Day = request.form["date"]

            query = "INSERT INTO Expenses (Name, Amount, Category, Description, Day) VALUES (%s, %s, %s, %s, %s)"

            cur = mysql.connection.cursor()
            cur.execute(query, (Name, Amount, Category, Description, Day))
            mysql.connection.commit()
        
        return redirect("/expenses")

# Listener

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5008))
    app.run(port=port, debug=True)