import time
import os
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
import sys
import yfinance as yf
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
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

def invite_to_portfolio(userid, portfolioid):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
                    INSERT INTO UserPortfolio(UsersUserID, PortfoliosPortfolioID)
                    VALUES (%s, %s)
                """, (userid, portfolioid))
        return "Invited"
    except Error as e:
        print(f"AU Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.commit()
            cursor.close()
            connection.close()
    return ("Invite Failed")


# adds new user profile to users table
def write_purchase(stock_symbol, portfolio_id, num_shares, purchase_price):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Transactions (CurrentlyActive, StockSymbol, NumShares, PurchasePrice, `DateTime`, PortfoliosPortfolioID)
            VALUES (1, %s, %s, %s, NOW(), %s);
        """, (stock_symbol, num_shares, purchase_price, portfolio_id))
        return True
    except Error as e:
        print(f"AU Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.commit()
            cursor.close()
            connection.close()
    return False


# adds new user profile to users table
def add_portfolio(portfolio_name):
    connection = None
    try:
        user_id = session['user']
        
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Portfolios (PortfolioType, PortfolioBalance)
            VALUES (%s, %s)
        """, (portfolio_name, 100000))

        portfolio_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO UserPortfolio (UsersUserID, PortfoliosPortfolioID)
            VALUES (%s, %s)
        """, (user_id, portfolio_id))

        return True
    except Error as e:
        print(f"AP Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.commit()
            cursor.close()
            connection.close()
    return False

# adds new user profile to users table
def sell_stock(transaction_id):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
                    UPDATE Transactions
                    SET CurrentlyActive = 0
                    WHERE TransactionID = %s
                """, (transaction_id,))
        print("stock sold")
        return True
    except Error as e:
        print(f"Sell Stock Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.commit()
            cursor.close()
            connection.close()

def remove_from_watch(portfolioid, stocksymbol):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
                    DELETE FROM Watchlist
                    WHERE PortfolioID = %s AND StockSymbol = %s
                """, (portfolioid, stocksymbol))
        print("watch removed")
        return True
    except Error as e:
        print(f"Watchlist Remove Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.commit()
            cursor.close()
            connection.close()


# adds new user profile to users table
def update_balance(new_balance, portfolio_id):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
                    UPDATE Portfolios
                    SET PortfolioBalance = %s
                    WHERE PortfolioID = %s
                """, (new_balance, portfolio_id))
        print("balance updated")
        return True
    except Error as e:
        print(f"Balance Update Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.commit()
            cursor.close()
            connection.close()


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
            SELECT PortfolioID, PortfolioType, PortfolioBalance
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

def get_most_val_stock():
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            CALL ownsMostValStock()
        """, params=None)
        return cursor.fetchall()
    except Error as e:
        error_message = e.msg
        print(f"ValStock Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return error_message

def get_stats_performers(date_start, date_end):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            CALL bestPerformers(%s,%s)
        """, (date_start, date_end))

        stats_data = cursor.fetchall()

        for stat in stats_data:
            percent = (stat['performance'] - 1) * 100
            stat['performance'] = f"{percent:.2f}%"
        
        return stats_data
    except Error as e:
        print(f"Performer Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return False

def get_sector_portfolios(sector):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            CALL sectorHeavy(%s)
        """, (sector,))
        return cursor.fetchall()
    except Error as e:
        error_message = e.msg
        print(f"sector_search Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return error_message

def get_company_search(search_str):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            CALL search(%s)
        """, (search_str,))
        return cursor.fetchall()
    except Error as e:
        error_code = e.errno
        error_message = e.msg
        print(f"KeySearch Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return error_message



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
            SELECT TransactionID, CurrentlyActive, StockSymbol, NumShares, PurchasePrice, DateTime
            FROM Portfolios JOIN Transactions ON PortfolioID=PortfoliosPortfolioID
            WHERE PortfolioID = %s
        """, (portfolioid,))
        for row in cursor:
            transaction_data.append(row)
        yfinance_data(transaction_data)
        calculate_change(transaction_data)

        return transaction_data
    except Error as e:
        print(f"GTD Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return False

def get_list_sectors():
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT DISTINCT Sector
            FROM Companies
        """,params=None)
        return cursor.fetchall()
    except Error as e:
        print(f"GLS Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return False

def calculate_change(array_of_stock_dicts):
    for stock_dict in array_of_stock_dicts:
        print(f"{stock_dict=}")
        purchase_price = stock_dict['PurchasePrice']
        current_price = stock_dict['CurrentPrice']
        num_shares = stock_dict['NumShares']

        percentage_change = ((current_price - purchase_price) / purchase_price * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        dollar_change = ((current_price - purchase_price) * num_shares).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        stock_dict['PercentChange'] = Decimal(percentage_change)
        stock_dict['DollarChange'] = Decimal(dollar_change)
    

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

        print(watchlist_data)

        user_id = session['user']

        hi_lo_dict = get_hi_lo_sp(portfolioid)

        print("this is hi lo:", hi_lo_dict)

        for stock in watchlist_data:

            stock_symbol = stock['StockSymbol']
            stock['High'] = hi_lo_dict[stock_symbol][0]
            stock['Low'] = hi_lo_dict[stock_symbol][1]

        print("watchlist with hi lo", watchlist_data)

        return watchlist_data
    except Error as e:
        print(f"GWD Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return False

def yfinance_data(array_of_stock_dicts):

    if len(array_of_stock_dicts) == 0:
        return

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

def get_stock_value_balance(transactions):
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

def add_stock_to_watchlist(stock_symbol, portfolioid):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Watchlist (StockSymbol, PortfolioID)
            VALUES (%s, %s)
        """, (stock_symbol, portfolioid))
        return True
    except Error as e:
        print(f"watchlist addition Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.commit()
            cursor.close()
            connection.close()
    return False

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


@app.route('/create_portfolio', methods=['GET', 'POST'])
def create_portfolio():
    if request.method == 'POST':
        portfolio_name = request.form['portfolio_name']
        if add_portfolio(portfolio_name):
                return redirect(url_for('dashboard', userid=session['user']))
    return render_template('create_portfolio.html')


@app.route('/portfolio/<portfolioid>', methods=['GET', 'POST'])
def portfolio_page(portfolioid):
    iMsg = ''
    if 'user' not in session:
        return redirect(url_for('login'))
    transaction_data = get_transaction_data(portfolioid)
    # print(transaction_data)
    portfolio_data = get_portfolio_type(portfolioid)
    watchlist_data = get_watchlist_data(portfolioid)
    sbalance = get_stock_value_balance(transaction_data)
    print(f'{portfolio_data}')
    if request.method == 'POST':
        if request.form['action'] =='invite':
            invitee = request.form['invite']
            portfolio_id = request.form['portfolio_id']

            print(f"{invitee=}")
            print(f"{portfolio_id=}")
            iMsg = invite_to_portfolio(invitee, portfolio_id)
            print(f'{iMsg}')
    return render_template('portfolio.html', transactions=transaction_data, watchlist=watchlist_data, portfolio=portfolio_data, sbalance=sbalance, iMsg=iMsg)


@app.route('/portfolio/<portfolioid>/add_watchlist', methods=['GET', 'POST'])
def add_watchlist(portfolioid):
    erMsg=''
    if request.method == 'POST':
        stock_symbol = request.form['stock_symbol']
        stock_symbol = stock_symbol.upper()
        exist, name = get_stock_name_from_symbol(stock_symbol)
        if exist:
            add_stock_to_watchlist(stock_symbol, portfolioid)
            return redirect(url_for('portfolio_page',  portfolioid=portfolioid))
        else:
            print("invalid stock")
            erMsg = "Not valid Stock Symbol. Please see company selector on Stats page."
    return render_template('add_watchlist.html', portfolioid=portfolioid, erMsg=erMsg)

@app.route('/transactions/<portfolioid>', methods=['GET'])
def transaction_page(portfolioid):
    if 'user' not in session:
        return redirect(url_for('login'))
    transaction_data = get_transaction_data(portfolioid)
    portfolio_type = get_portfolio_type(portfolioid)
    return render_template('transaction.html', transactions=transaction_data, portfolio=portfolio_type)

@app.route('/stats/', methods=['GET', 'POST'])
def stats():
    msg1=''
    stats_data_performers=''
    companyResult=''
    searchErMsg=''
    portfolios=''
    sectorErMsg=''
    sector=''
    valStocks=get_most_val_stock()
    print(f'{valStocks=}')
    sectors = get_list_sectors()
    print(f'{sectors=}')
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        if request.form['action'] =='dateSearch':
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            print(f'{start_date=}')
            print(f'{end_date=}')
            erMsg = verify_date_search(start_date, end_date)
            print(f'{msg1}')
            stats_data_performers = get_stats_performers(start_date,end_date)
            print(f'{stats_data_performers=}')
        if request.form['action'] =='companySearch':
            companystr = request.form['companySearch']
            print(f'{companystr=}')
            companyResult = get_company_search(companystr)
            print(f'{companyResult=}')
            if isinstance(companyResult,str):
                searchErMsg = companyResult
                companyResult =''
            print(f'{searchErMsg=}')
        if request.form['action'] =='sectors':
            sector = request.form['sectors']
            portfolios = get_sector_portfolios(sector)
            print(f'{portfolios=}')
            if isinstance(portfolios,str):
                sectorErMsg = portfolios
                portfolios =''

    return render_template('stats.html', msg1=msg1, performers=stats_data_performers, keysearch=companyResult,searchErMsg=searchErMsg,  
                           sectors=sectors, Sportfolios=portfolios, sectorErMsg=sectorErMsg, sector=sector, valStocks=valStocks)

def format_date_from_str(datestr):
    input_format = "%Y-%m-%d"
    datetime_type = datetime.strptime(datestr, "%Y-%m-%d")
    date_type = datetime_type.date()
    print(date_type)
    return date_type

def verify_date_search(startdate, enddate):
    msg=''
    startdate = format_date_from_str(startdate)
    enddate = format_date_from_str(enddate)
    if(enddate < startdate):
        msg = "End Date needs to be after Start Date"
    elif(startdate < date(2010,1,4)):
        msg = "Start Date needs to be after 01-04-2010"
    elif(enddate > date(2024,7,15)):
        msg = "End Date needs to be before 07-15-2024"
    return msg

#main intent is to get the transaction id to modify it
#idk how to get the transaction data
#use portfolio id? then query transactions? or more direct way to do it?

@app.route('/sell', methods=['GET','POST'])
def sell_shares():
    portfolio_id=''
    if request.form['action'] =='sell':
        transaction_id = request.form.get('transaction_id')
        portfolio_id = request.form.get('portfolio_id')
        stock_current_price = Decimal(request.form.get('stock_current_price'))
        num_shares = int(request.form.get('num_shares'))
        portfolio_balance = Decimal(request.form.get('portfolio_balance'))

        print(f"{portfolio_id=}")
        print(f"{transaction_id=}")
        print(f"{stock_current_price=}")
        print(f"{num_shares=}")
        print(f"{portfolio_balance=}")

        value_of_sale = stock_current_price * num_shares

        new_balance = portfolio_balance + value_of_sale
        
        print(f"{value_of_sale=}")
        print(f"{new_balance=}")

        sell_stock(transaction_id)

        update_balance(new_balance, portfolio_id)
    return redirect(url_for('portfolio_page', portfolioid=portfolio_id))

@app.route('/remove_watch', methods=['GET','POST'])
def remove_watch():
    portfolio_id = ''
    if request.form['action'] =='remove':
        stock_symbol = request.form.get('stock_symbol')
        portfolio_id = request.form.get('portfolio_id')

        print(f"{stock_symbol=}")
        print(f"{portfolio_id=}")
        remove_from_watch(portfolio_id, stock_symbol)
    return redirect(url_for('portfolio_page', portfolioid=portfolio_id))

# @app.route('/invite_user', methods=['GET','POST'])
# def invite_user():
#     portfolio_id = ''
#     if request.form['action'] =='invite':
#         invitee = request.form.get('invite')
#         portfolio_id = request.form.get('portfolio_id')

#         print(f"{invitee=}")
#         print(f"{portfolio_id=}")
#         iMsg = invite_to_portfolio(invitee, portfolio_id)
#     return redirect(url_for('portfolio_page', portfolioid=portfolio_id))



@app.route('/portfolio/<portfolioid>/buy', methods=['GET', 'POST'])
def buy_stock(portfolioid):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    stock_symbol = ''
    num_shares = ''
    stock_name = ''
    current_price = Decimal(0)
    value_of_buy = 0
    confirmed = False


    portfolio_data = get_portfolio_type(portfolioid)

    if request.method == 'POST':

        stock_symbol = request.form.get('stock_symbol').upper()
        try:
            num_shares = int(request.form.get('num_shares'))
        except Exception as e:
            print("Error, not an int: ", e)
            num_shares = 0
            stock_name = "Please enter an integer number of shares"

        if 'confirm_stock' in request.form:

            if num_shares < 1:
                stock_name = "Invalid number of shares"
            else: 
                exists, stock_name = get_stock_name_from_symbol(stock_symbol)

                if exists:
                    current_price = get_stock_current_price(stock_symbol)
                    value_of_buy = current_price * num_shares 

                    cash_balance = get_portfolio_type(portfolioid)['PortfolioBalance']
                    if value_of_buy < cash_balance:
                        confirmed = True
                    else:
                        stock_name = "Not enough cash for purchase:"
                else:
                    stock_name += ". Please see company selector on Stats page."

            
        elif 'place_order' in request.form:

            if num_shares < 1:
                stock_name = "Invalid number of shares"
            else: 
                exists, stock_name = get_stock_name_from_symbol(stock_symbol)

                if exists:
                    current_price = get_stock_current_price(stock_symbol)
                    value_of_buy = current_price * num_shares 
                else:
                    stock_name += ". Please see company selector on Stats page."

                
                
                cash_balance = get_portfolio_type(portfolioid)['PortfolioBalance']
                # print(f"{cash_balance=}")
                # print(f"{value_of_buy=}")


                if value_of_buy < cash_balance:
                    new_balance = cash_balance - value_of_buy
                    update_balance(new_balance, portfolioid)

                    write_purchase(stock_symbol, portfolioid, num_shares, current_price)

                    return redirect(url_for('portfolio_page', portfolioid=portfolioid))
                else:
                    print("purchase not possible")

    return render_template('buy_stock.html', portfolio=portfolio_data, msg=stock_name, stock_symbol=stock_symbol, num_shares=num_shares, stock_price=current_price, purchase_cost=value_of_buy, confirmed=confirmed)







def get_stock_current_price(stock_symbol):

    while True:
        try:
            data = yf.download(stock_symbol, period="1d", interval="1m")

            if not data.empty:
                watchlist_prices = data['Adj Close'].iloc[-1]
                current_price = Decimal("{:.2f}".format(watchlist_prices))
                return current_price
            
            time.sleep(1)

        except Exception as e:
            print("Error with yfinance API:", str(e))
    



def get_stock_name_from_symbol(stock_symbol):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
                    SELECT Name
                    FROM Companies
                    WHERE StockSymbol = %s
                """, (stock_symbol,))
        stock_name = cursor.fetchone()
        if stock_name:
            return (True, stock_name[0])
        else:
            return (False, "Stock not in S&P 500")
    except Error as e:
        print(f"get stock name from symbol Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()



def get_hi_lo(portfolio_id):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT w.StockSymbol, 
                MAX(hs.ClosePrice) AS HighPrice, 
                MIN(hs.ClosePrice) AS LowPrice
            FROM Users u
            JOIN UserPortfolio up ON u.UserID = up.UsersUserID
            JOIN Watchlist w ON up.PortfoliosPortfolioID = w.PortfolioID
            JOIN HistoricalStocks hs ON w.StockSymbol = hs.StockSymbol
            WHERE w.PortfolioID = %s
                AND hs.Date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY u.UserID, w.StockSymbol
                """, (portfolio_id))
        stock_hi_lo = []
        for row in cursor:
            stock_hi_lo.append(row)

        hi_lo_dict = {}
        for symbol, high, low in stock_hi_lo:
            hi_lo_dict[symbol] = (high, low)

        return hi_lo_dict
    
    except Error as e:
        print(f"get stock name from symbol Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def get_hi_lo_sp(portfolio_id):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("CALL watchlistMinMax(%s)", (portfolio_id,))
        stock_hi_lo = []
        for row in cursor:
            stock_hi_lo.append(row)

        hi_lo_dict = {}
        for symbol, high, low in stock_hi_lo:
            hi_lo_dict[symbol] = (high, low)

        return hi_lo_dict
    
    except Error as e:
        print(f"get stock name from symbol Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
