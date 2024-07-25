#https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html

"""
    This file DOES NOT run. 
    DO NOT attach to TradingPaper
    This is only to look at functions we may need to use
"""

import mysql.connector
from mysql.connector import Error

"""
    How to  connect to MySQL Server
    Put line that attempts to connect into try block to handle any errors
    Define connection arguements into dict and use **
    """
config = {
    'host': 'IP', #'34.42.241.176' in our case
    'user': 'root',
    'password': 'PW',  # test1234
    'database': 'dbName' #TradingPaper
}
#https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html
#connection arguement list
def tryConnect(con):
    try:
        cnx = mysql.connector.connect(**con)
        #write code here
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

cnx = tryConnect(config)


"""To make a cursor"""
cursor = cnx.cursor()
cursor.execute(
    # any other SQL code
    )
cursor.close()
cnx.close()



from datetime import date, datetime, timedelta
"""Inserting Data"""
cnx = tryConnect(config)
cursor = cnx.cursor()
add_employee = ("INSERT INTO employees "
               "(first_name, last_name, hire_date, gender, birth_date) "
               "VALUES (%s, %s, %s, %s, %s)")
data_employee = ('Geert', 'Vanderkelen', date(1999, 12, 1999), 'M', date(1977, 6, 14))
cursor.execute(add_employee, data_employee)
cnx.commit()
cursor.close()
cnx.close()

"""Querying Data"""
cnx = tryConnect(config)
cursor = cnx.cursor()
query = ("SELECT first_name, last_name, hire_date FROM employees "
         "WHERE hire_date BETWEEN %s AND %s")
hire_start = datetime.date(1999, 1, 1)
hire_end = datetime.date(1999, 12, 31)
cursor.execute(query, (hire_start, hire_end))

#How we can possible display information
for (first_name, last_name, hire_date) in cursor:
  print("{}, {} was hired on {:%d %b %Y}".format(
    last_name, first_name, hire_date))
cursor.close()
cnx.close()


"""Flask"""
# https://flask.palletsprojects.com/en/3.0.x/quickstart/#a-minimal-application

"""Any user-provided values rendered in the output must be escaped to protect from injection attacks"""
from markupsafe import escape
@app.route("/<name>")
def hello(name):
    return f"Hello, {escape(name)}!"

""""Use the route() decorator to bind a function to a URL"""
@app.route('/')
def index():
    return 'Index Page'
#http://127.0.0.1:5000/
@app.route('/hello')
def hello():
    return "hello, wrld"
#http://127.0.0.1:5000/hello


"""Rendering Templates"""
from flask import render_template

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', person=name)