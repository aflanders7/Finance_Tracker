from flask import Flask, render_template, json, redirect, request
import database.db_connector as db
import requests
import psycopg2


# Configuration

app = Flask(__name__)
db_connection = db.connect_to_database()


# Routes 

@app.route('/')
def root():
    return redirect("/graph")

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

        query2 = 'SELECT SUM(Amount) FROM Expenses;'
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
        
# route for income page

@app.route('/income', methods=["POST", "GET"])
def income():
    if request.method == "GET":

        query = "SELECT * FROM Income ORDER BY Day DESC;"
        data = db.get_data(query)

        query2 = 'SELECT SUM(Amount) FROM Income;'
        total = db.get_data(query2)
        
        return render_template("income.j2", Income=data, total=total)

    if request.method == "POST":

        if request.form.get("Add_Income"):
            Name = request.form["name"]
            Amount = request.form["amount"]
            Description = request.form["description"]
            Day = request.form["date"]
        
            if Description == "":
                query = "INSERT INTO Income (Name, Amount, Day) VALUES (%s, %s, %s);"
                db.commit_data_values(query, (Name, Amount, Day))

            else:
                query = "INSERT INTO Income (Name, Amount, Description, Day) VALUES (%s, %s, %s, %s);"
                db.commit_data_values(query, (Name, Amount, Description, Day))
            
            return redirect("/income")


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

# route for sorting on income page

@app.route('/income-sort', methods=["GET"])
def income_sort():
    if request.method == "GET":
        query = "SELECT * FROM Income ORDER BY Amount;"  
        
        data = db.get_data(query)
        query2 = 'SELECT SUM(Amount) FROM Income'
        total = db.get_data(query2)
        
        return render_template("income.j2", Income=data, total=total)

# route for search function on expenses page

@app.route('/expenses-search', methods=["POST"])
def search_expense():
    if request.method == "POST":
        Name = request.form["searchName"]
        if Name == "":
            return redirect("/expenses")

        query = "SELECT * FROM Expenses WHERE Name ILIKE "'%s'";"
        data = db.get_data_values(query, (Name,))

        query2 = "SELECT SUM(Amount) FROM Expenses WHERE Name ILIKE "'%s'";"
        total = db.get_data_values(query2, (Name,))
        
        return render_template("expenses.j2", Expenses=data, total=total)
    
# route for search function on income page

@app.route('/income-search', methods=["POST"])
def search_income():
    if request.method == "POST":
        Name = request.form["searchName"]
        if Name == "":
            return redirect("/income")

        query = "SELECT * FROM Income WHERE Name ILIKE "'%s'";"
        data = db.get_data_values(query, (Name,))

        query2 = "SELECT SUM(Amount) FROM Income WHERE Name ILIKE "'%s'";"
        total = db.get_data_values(query2, (Name,))
        
        return render_template("income.j2", Income=data, total=total)

# routes for deletions 

@app.route('/delete_expense/<int:id>')
def delete_expense(id):
    query = "DELETE FROM Expenses where ID = '%s';"
    db.commit_data_values(query, (id,))
    return redirect("/expenses")

@app.route('/delete_income/<int:id>')
def delete_income(id):
    query = "DELETE FROM Income where ID = '%s';"
    db.commit_data_values(query, (id,))
    return redirect("/income")


# routes for graph page

@app.route('/graph', methods=["GET"])
def graph():
    if request.method == "GET":

        query = 'SELECT SUM(expense) as Expense, SUM(incomes) as Income, CAST(Month AS Int), CAST (Year AS Int) FROM (SELECT Extract(Month FROM Expenses.Day) AS Month, Extract(Year FROM Expenses.Day) AS Year, Expenses.amount as expense, 0 as incomes FROM Expenses UNION ALL SELECT Extract(Month FROM Income.Day) AS Month, Extract(Year FROM Income.Day) AS Year, 0 as expense, Income.amount as incomes FROM Income) as data GROUP BY data.Month, data.Year ORDER BY data.YEAR, data.MONTH;'
        data = db.get_data(query)

        expense, income, months, years = zip(*data)

        labels = get_month_labels(months, years)
        net_income = get_net(expense, income)
        
        query2 = 'SELECT SUM(Amount) FROM Expenses;'
        total = db.get_data(query2)

        query3 = 'SELECT SUM(Amount) FROM Income;'
        total2 = db.get_data(query3)

        net_balance = (total2[0][0]) - (total[0][0])

        categories = microservice()
        labels2 = list(categories.keys())
        data2 = list(categories.values())

        return  render_template("graph.html", labels=labels, data=expense, data1=income, total=net_balance, labels2=labels2, data2=data2, data3=net_income)

def get_month_labels(dates, years):
    MONTHS = ['January','February','March','April','May','June','July','August','September','October',
        'November','December']
     
    data_labels = []
    for index in range(len(dates)):     # get the list of months and years to use as labels
        month_val = dates[index] - 1
        data_labels.append(MONTHS[month_val] + " " + str(years[index]))   

    return data_labels

def get_net(expense, income):
    net_income = []
    total = 0
    for index in range(len(expense)):
        net = total + income[index] - expense[index] 
        net_income.append(int(net))
        total = net
    return net_income


# microservice setup

url = "http://127.0.0.1:3008/" #microservice url


def microservice():
    query = 'SELECT CAST(SUM(Amount) AS INT), Category FROM Expenses GROUP BY Category;'
    data = db.get_data(query)
    print(data)
    # microservice removed for deployment 
    # result = call_the_microservice(data)
    result = get_percentages(data)
    return result

def call_the_microservice(list):  
    response = requests.get(url, params={'catlist': list})
    percent = response.json().get("result")
    return percent

def get_percentages(data):    
    result = {}
    cost = 0

    # determine total cost
    for i in range(0, len(data)):
        cost += float(data[i][0])

    # calculate percentage of total cost each category accounts for
    for i in range(0, len(data)):
        result[data[i][1]] = round(float(data[i][0])/cost * 100, 0)

    return result


# Listener

if __name__ == "__main__":
	app.run(port=5008)