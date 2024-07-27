import os
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
import sys
app = Flask(__name__)
app.secret_key = 'your_secret_key' #DO NOT DELETER: need this to work for some reason



# Database connection parameters
config = {
    'host': '34.42.241.176',
    'user': 'root',
    'password': 'test1234',
    'database': 'TradingPaper'
}

def get_db_connection():
    connection = mysql.connector.connect(**config)
    return connection
            

@app.route('/')
def index():
    return render_template('index.html')

# Checks whether the userid and password are valid
def valid_login(userid, password):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT UserID, Password, FullName
            FROM Users
            WHERE UserID = %s AND Password = %s
        """, (userid, password))
        user = cursor.fetchone()
        return user
    except Error as e:
        print(f"VL Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return False

# Checks if userid is in users table
def user_exist(userid):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
                    SELECT UserID
                    FROM Users
                    WHERE UserID = %s
                """, (userid,))
        return cursor.fetchone()
    except Error as e:
        print(f"UE Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return False

# adds new user profile to users table
def add_user(userid, password, address, phonenumber, fullname):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
                    INSERT INTO Users(UserID, Password, Address, PhoneNumber, FullName)
                    VALUES (%s, %s, %s, %s, %s)
                """, (userid, password, address, phonenumber, fullname))
        return True
    except Error as e:
        print(f"AU Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.commit()
            cursor.close()
            connection.close()
    return False

def get_portfolio_data(userid):
    connection = None
    try:
        portfolio_data = []
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT PortfolioType, PortfolioBalance
            FROM Users JOIN UserPortfolio ON UserID=UsersUserID 
                       JOIN Portfolios ON PortfolioID=PortfoliosPortfolioID
            WHERE UserID = %s
        """, (userid,))
        for row in cursor:
            portfolio_data.append(row)
        return portfolio_data
    except Error as e:
        print(f"GPD Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return False


"""random user to test with"""
# user: adam44
# password: (%L45Ka#+4
@app.route('/login', methods=['GET', 'POST'])
def login():
    erMsg = ''
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        user = valid_login(userid,password)
        if user:
            session['user'] = user['UserID']
            return redirect(url_for('dashboard', username = user['FullName']))
        else:
            if user_exist(userid):
                erMsg = "Login failed: Incorrect password"
            else:
                erMsg = "Login failed: UserID does not exist"
    return render_template('login.html', msg=erMsg)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    erMsg = ''
    if request.method == 'POST':
        userid = request.form['userid']
        if user_exist(userid):
            erMsg = "UserID already exists"
        else:
            password = request.form['password']
            address = request.form['address']
            phonenumber = request.form['phonenumber']
            fullname = request.form['fullname']
            if add_user(userid, password, address, phonenumber, fullname):
                return redirect(url_for('login', msg=''))
    return render_template('signup.html', msg=erMsg)


@app.route('/dashboard', methods=['GET', 'POST'])
@app.route('/dashboard/<username>/', methods=['GET', 'POST'])
def dashboard(username):
    portfolio_data = []
    if 'user' not in session:
        return redirect(url_for('login'))
    userid = session['user']
    portfolio_data = get_portfolio_data(userid)
    return render_template('dash.html', portfolios=portfolio_data, username=username)
    
# @app.route('/db-test')
# def db_test():
#     connection = None
#     try:
#         connection = get_db_connection()
#         if connection.is_connected():
#             db_info = connection.get_server_info()
#             return f'Connected to MySQL database... MySQL Server version: {db_info}'
#     except Error as e:
#         return f'Error while connecting to MySQL: {e}'
#     finally:
#         if connection and connection.is_connected():
#             connection.close()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
