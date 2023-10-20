from flask import Flask, render_template, json
import os
import database.db_connector as db

db_connection = db.connect_to_database()

# Configuration

app = Flask(__name__)

# Routes 

@app.route('/')
def root():
    return render_template("main.j2")

@app.route('/test')
def income():
    query = "SELECT * FROM Income;"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    results = json.dumps(cursor.fetchall())
    return results

# Listener

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5008))
    app.run(port=port, debug=True)