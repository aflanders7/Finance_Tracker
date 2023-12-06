import MySQLdb 
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

host = os.environ.get("host")
user = os.environ.get("user")
passwd = os.environ.get("passwd")
db = os.environ.get("db")

db_connection = MySQLdb.connect(host,user,passwd,db)

def connect_to_database(host = host, user = user, passwd = passwd, db = db):
    db_connection = MySQLdb.connect(host,user,passwd,db)
    return db_connection

def get_data(query):
    cur = db_connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    return data

def get_data_values(query, values):
    cur = db_connection.cursor()
    cur.execute(query, values)
    data = cur.fetchall()
    return data

def commit_data_values(query, values):
    cur = db_connection.cursor()
    cur.execute(query, values)
    db_connection.commit()
