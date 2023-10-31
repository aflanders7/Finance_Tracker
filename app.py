from flask import Flask, render_template, json, redirect, request
import os
import database.db_connector as db

db_connection = db.connect_to_database()

# Configuration

app = Flask(__name__)

# Routes 

@app.route('/')
def root():
    return redirect("/expenses")

@app.route('/expenses', methods=["POST", "GET"])
def expense():
    if request.method == "GET":
        query = "SELECT Name, Amount, Category, Description, Day FROM Expenses;"
        cursor = db.execute_query(db_connection=db_connection, query=query)
        data = cursor.fetchall()
        return render_template("expenses.j2", Expenses=data)

    if request.method == "POST":
        if request.form.get("Add_Expense"):
            Name = request.form["name"]
            Amount = request.form["amount"]
            Category = request.form["category"]
            Description = request.form["description"]
            Day = request.form["date"]


            query = "INSERT INTO Expenses (Name, Amount, Category, Description, Day) VALUES (%s, %s, %s, %s, %s)"
            cursor = db.execute_query(db_connection=db_connection, query=query)
        
        return redirect("/expenses")

# Listener

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5008))
    app.run(port=port, debug=True)