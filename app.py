from flask import Flask, render_template, json, redirect, request
import database.db_connector as db
import requests


# Configuration

app = Flask(__name__)
db_connection = db.connect_to_database()


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
        data = db.get_data(query)

        query2 = 'SELECT SUM(Amount) FROM Expenses'
        total = db.get_data(query2)
        
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
                db.commit_data_values(query, (Name, Amount, Category, Day))

            else:
                query = "INSERT INTO Expenses (Name, Amount, Category, Description, Day) VALUES (%s, %s, %s, %s, %s);"
                db.commit_data_values(query, (Name, Amount, Category, Description, Day))
            
            return redirect("/expenses")


# route for sorting on expenses page

@app.route('/expenses-sort', methods=["GET"])
def expense_sort():
    if request.method == "GET":
        value = request.args["sort"]

        if value == "Category":
            query = "SELECT * FROM Expenses ORDER BY Category;" 

        elif value == "Cost":
            query = "SELECT * FROM Expenses ORDER BY Amount;"  
        
        data = db.get_data(query)
        query2 = 'SELECT SUM(Amount) FROM Expenses'
        total = db.get_data(query2)
        
        return render_template("expenses.j2", Expenses=data, total=total)


# route for search function on expenses page

@app.route('/expenses-search', methods=["POST"])
def search_expense():
    if request.method == "POST":
        Name = request.form["searchName"]
        if Name == "":
            return redirect("/expenses")

        query = "SELECT * FROM Expenses WHERE Name LIKE "'%s'";"
        data = db.get_data_values(query, (Name,))

        query2 = "SELECT SUM(Amount) FROM Expenses WHERE Name LIKE "'%s'";"
        total = db.get_data_values(query2, (Name,))
        
        return render_template("expenses.j2", Expenses=data, total=total)

# route for deletion on expenses page table

@app.route('/delete_expense/<int:id>')
def delete_expense(id):
    query = "DELETE FROM Expenses where ID = '%s';"
    db.commit_data_values(query, (id,))
    return redirect("/expenses")


# routes for graph page

@app.route('/graph', methods=["GET"])
def graph():
    if request.method == "GET":

        query = 'SELECT SUM(Amount), MONTH(Day), YEAR(Day) FROM Expenses GROUP BY YEAR(Day), MONTH(DAY);'
        data = db.get_data(query)

        money, dates, years = zip(*data)
        labels = get_month_labels(dates, years)
        
        query2 = 'SELECT SUM(Amount) FROM Expenses'
        total = db.get_data(query2)

        categories = microservice()
        labels2 = list(categories.keys())
        data2 = list(categories.values())

        return  render_template("graph.html", labels=labels, data=money, total=total, labels2=labels2, data2=data2)

def get_month_labels(dates, years):
    MONTHS = ['January','February','March','April','May','June','July','August','September','October',
        'November','December']
     
    data_labels = []
    for index in range(len(dates)):     # get the list of months and years to use as labels
        month_val = dates[index] - 1
        data_labels.append(MONTHS[month_val] + " " + str(years[index]))   

    return data_labels


# microservice setup

url = "http://127.0.0.1:3008/" #microservice url


def microservice():
    query = 'SELECT SUM(Amount), Category FROM Expenses GROUP BY Category;'
    data = db.get_data(query)
    result = call_the_microservice(data)
    return result

def call_the_microservice(list):  
    response = requests.get(url, params={'catlist': list})
    percent = response.json().get("result")
    return percent


# Listener

if __name__ == "__main__":
	app.run(port=5008)