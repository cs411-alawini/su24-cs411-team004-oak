import os
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
import sys
import yfinance as yf
from decimal import Decimal
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
            SELECT PortfolioID, PortfolioType, PortfolioBalance
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

def get_portfolio_type(portfolioid):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT PortfolioID, PortfolioType
            FROM Portfolios
            WHERE PortfolioID = %s
        """, (portfolioid,))
        return cursor.fetchone()
    except Error as e:
        print(f"GPT Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return False

def get_fullname(userid):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT Fullname
            FROM Users
            WHERE UserID = %s
        """, (userid,))
        return cursor.fetchone()
    except Error as e:
        print(f"GF Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return False

def get_transaction_data(portfolioid):
    connection = None
    try:
        transaction_data = []
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT CurrentlyActive, StockSymbol, NumShares, PurchasePrice, DateTime
            FROM Portfolios JOIN Transactions ON PortfolioID=PortfoliosPortfolioID
            WHERE PortfolioID = %s
        """, (portfolioid,))
        for row in cursor:
            transaction_data.append(row)
        yfinance_data(transaction_data)

        return transaction_data
    except Error as e:
        print(f"GPD Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return False

def get_watchlist_data(portfolioid):
    connection = None
    try:
        watchlist_data = []
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT w.StockSymbol
            FROM Portfolios p JOIN Watchlist w ON p.PortfolioID=w.PortfolioID
            WHERE p.PortfolioID = %s
        """, (portfolioid,))
        for row in cursor:
            watchlist_data.append(row)
        yfinance_data(watchlist_data)

        return watchlist_data
    except Error as e:
        print(f"GWD Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return False

def yfinance_data(array_of_stock_dicts):

    stock_symbols = []
    for stock_dict in array_of_stock_dicts:
        stock_symbols.append(stock_dict['StockSymbol'])

    try:
        data = yf.download(stock_symbols, period="1d", interval="1m")

        if data.empty:
            print("No data")
        else:
            #gets only the adjusted close
            watchlist_prices = data['Adj Close'].iloc[-1]

            #seperate logic for yfinance API 
            #when one only one stock symbol is requested it does not return a data frame, only the price itself
            if len(stock_symbols) == 1:
                array_of_stock_dicts[0]['CurrentPrice'] = Decimal("{:.2f}".format(watchlist_prices))
            else: 
                watchlist_price_dict = watchlist_prices.to_dict()
                #loops through array of stocks to assign values to corresponding stock in the dictionary rounded to 2 decimals
                for stock_dict in array_of_stock_dicts:
                    current_stock = stock_dict['StockSymbol']
                    stock_dict['CurrentPrice'] = Decimal("{:.2f}".format(watchlist_price_dict.get(current_stock)))

    except Exception as e:
        print("Error with yfinance API:", str(e))

def get_portfolio_balance(transactions):
    total_balance = 0
    if(len(transactions) > 0):
        for transaction in transactions:
            if(transaction['CurrentlyActive']):
                total_balance += transaction['NumShares'] * transaction['CurrentPrice']
    return total_balance

def get_dashboard_balance(portfolios):
    total_balance = 0
    if(len(portfolios) > 0):
        for portfolio in portfolios:
            total_balance += portfolio['PortfolioBalance']
    return total_balance

"""random user to test with"""
# user: aaron16
# password: ho^_7BnNS^
@app.route('/login', methods=['GET', 'POST'])
def login():
    session['user']=None
    erMsg = ''
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        user = valid_login(userid,password)
        if user:
            session['user'] = user['UserID']
            return redirect(url_for('dashboard', userid = user['UserID']))
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


@app.route('/dashboard', methods=['GET'])
@app.route('/dashboard/<userid>/', methods=['GET'])
def dashboard(userid):
    portfolio_data = []
    if 'user' not in session:
        return redirect(url_for('login'))
    userid = session['user']
    portfolio_data = get_portfolio_data(userid)
    fullname = get_fullname(userid)
    dbalance = get_dashboard_balance(portfolio_data)
    return render_template('dash.html', portfolios=portfolio_data, fullname=fullname['Fullname'], dbalance=dbalance)


@app.route('/portfolio/<portfolioid>', methods=['GET'])
def portfolio_page(portfolioid):
    if 'user' not in session:
        return redirect(url_for('login'))
    transaction_data = get_transaction_data(portfolioid)
    print(transaction_data)
    portfolio_type = get_portfolio_type(portfolioid)
    watchlist_data = get_watchlist_data(portfolioid)
    pbalance = get_portfolio_balance(transaction_data)
    return render_template('portfolio.html', transactions=transaction_data, watchlist=watchlist_data, portfolio=portfolio_type, pbalance=pbalance)

@app.route('/transactions/<portfolioid>', methods=['GET'])
def transaction_page(portfolioid):
    if 'user' not in session:
        return redirect(url_for('login'))
    transaction_data = get_transaction_data(portfolioid)
    portfolio_type = get_portfolio_type(portfolioid)
    return render_template('transaction.html', transactions=transaction_data, portfolio=portfolio_type)


# https://www.geeksforgeeks.org/how-to-use-flask-session-in-python-flask/
# @app.route("/logout")
# def logout():
#     session["name"] = None
#     return redirect("/")
    
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
