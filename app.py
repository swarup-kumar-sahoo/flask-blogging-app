# Store this code in 'app.py' file
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re


app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'swarup72'
app.config['MYSQL_DB'] = 'logactivity'
app.secret_key = 'your secret key'

# Initialize MySQL with error handling
mysql = MySQL(app)

# Test database connection
def test_db_connection():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        print("Database connection successful!")
        return True
    except MySQLdb.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return False

# Check database connection before each request
@app.before_request
def check_db_connection():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
    except MySQLdb.Error as e:
        print(f"Database connection error: {e}")
        if not request.endpoint or request.endpoint not in ['static']:
            return 'Database connection failed. Please try again later.', 500


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['msg'] = 'Logged in successfully!'
            return redirect(url_for('index'))
        else:
            session['msg'] = 'Incorrect username / password!'
            return redirect(url_for('login'))
    
    msg = session.pop('msg', '')  # Get and remove the message from session
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if all(field in request.form for field in ['username', 'password', 'email', 
                                                 'college', 'city', 'state', 'country']):
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            college = request.form['college']
            city = request.form['city']
            state = request.form['state']
            country = request.form['country']
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            account = cursor.fetchone()
            
            if account:
                session['msg'] = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                session['msg'] = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                session['msg'] = 'Username must contain only characters and numbers!'
            else:
                cursor.execute('INSERT INTO accounts (username, password, email, college, city, state, country) \
                             VALUES (%s, %s, %s, %s, %s, %s, %s)',
                             (username, password, email, college, city, state, country))
                mysql.connection.commit()
                session['msg'] = 'You have successfully registered!'
                return redirect(url_for('login'))
            
            return redirect(url_for('register'))
        else:
            session['msg'] = 'Please fill out all required fields!'
            return redirect(url_for('register'))
    
    msg = session.pop('msg', '')  # Get and remove the message from session
    return render_template('register.html', msg=msg)


@app.route("/index")
def index():
    if 'loggedin' in session:
        return render_template("index.html")
    return redirect(url_for('login'))


@app.route("/display")
def display():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template("display.html", account=account)
    return redirect(url_for('login'))


@app.route("/update", methods=['GET', 'POST'])
def update():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if all(field in request.form for field in ['username', 'password', 'email', 
                                                 'college', 'city', 'state', 'country']):
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            college = request.form['college']
            city = request.form['city']
            state = request.form['state']
            country = request.form['country']
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = %s AND id != %s', 
                         (username, session['id']))
            account = cursor.fetchone()
            
            if account:
                session['msg'] = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                session['msg'] = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                session['msg'] = 'Username must contain only characters and numbers!'
            else:
                cursor.execute('UPDATE accounts SET username = %s, password = %s, email = %s, '
                           'college = %s, city = %s, state = %s, country = %s WHERE id = %s',
                           (username, password, email, college, city, state, country, session['id']))
                mysql.connection.commit()
                session['username'] = username  # Update session username
                session['msg'] = 'You have successfully updated your account!'
                return redirect(url_for('display'))
            
            return redirect(url_for('update'))
        else:
            session['msg'] = 'Please fill out all required fields!'
            return redirect(url_for('update'))
    
    msg = session.pop('msg', '')  # Get and remove the message from session
    return render_template("update.html", msg=msg)


@app.route("/viewmore")
def viewmore():
    if 'loggedin' in session:
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # Fetch all users except the current user's sensitive information
            cursor.execute('''
                SELECT id, username, email, organisation, city, state, country 
                FROM accounts 
                WHERE id != %s
                ORDER BY username
            ''', (session['id'],))
            users = cursor.fetchall()
            
            # Get current user's full details
            cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
            current_user = cursor.fetchone()
            
            return render_template(
                "viewmore.html",
                users=users,
                current_user=current_user,
                msg=''
            )
        except Exception as e:
            return render_template("viewmore.html", msg='An error occurred while fetching user data.')
        finally:
            cursor.close()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host="localhost", port=int("5000"))