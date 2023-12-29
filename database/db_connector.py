import psycopg2
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

host = os.environ.get("host")
user = os.environ.get("user")
passwd = os.environ.get("passwd")
db = os.environ.get("db")

db_connection = psycopg2.connect(dbname = db, user= user, password = passwd, host = host)

def connect_to_database(dbname = db, user= user, password = passwd, host = host):
    db_connection = psycopg2.connect(dbname = db, user= user, password = passwd, host = host)
    return db_connection

# query functions

def get_data(query):
    cur = db_connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data

def get_data_values(query, values):
    cur = db_connection.cursor()
    cur.execute(query, values)
    data = cur.fetchall()
    cur.close()
    return data

def commit_data_values(query, values):
    cur = db_connection.cursor()
    cur.execute(query, values)
    db_connection.commit()
