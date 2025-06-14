# Store this code in 'app.py' file
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import secrets
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_CONFIG
import logging
from datetime import timedelta
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.permanent_session_lifetime = timedelta(minutes=60)  # Session timeout

# Production configs
app.config.update(
    MYSQL_HOST=DB_CONFIG['host'],
    MYSQL_USER=DB_CONFIG['user'],
    MYSQL_PASSWORD=DB_CONFIG['password'],
    MYSQL_DB=DB_CONFIG['database'],
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

mysql = MySQL(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def close_db_connection(connection):
    if connection:
        connection.close()


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                return render_template('login.html', msg='Please fill all fields')
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            account = cursor.fetchone()
            
            if account and check_password_hash(account['password'], password):
                session.permanent = True
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                logger.info(f"User {username} logged in successfully")
                return redirect(url_for('index'))
            
            logger.warning(f"Failed login attempt for user {username}")
            return render_template('login.html', msg='Invalid credentials')
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return render_template('login.html', msg='An error occurred')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            collage = request.form['collage']
            city = request.form['city']
            state = request.form['state']
            country = request.form['country']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT * FROM accounts WHERE username = % s', (username, ))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'name must contain only characters and numbers !'
            else:
                # Hash the password before storing
                hashed_password = generate_password_hash(password)
                
                cursor.execute(
                    'INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)', 
                    (username, hashed_password, email, collage, city, state, country)
                )
                mysql.connection.commit()
                logger.info(f"New user registered: {username}")
                msg = 'You have successfully registered!'
                return redirect(url_for('login'))
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        msg = 'An error occurred during registration'
    finally:
        if 'cursor' in locals():
            cursor.close()
    
    return render_template('register.html', msg=msg)


@app.route("/index")
def index():
    if 'loggedin' in session:
        return render_template("index.html")
    return redirect(url_for('login'))


@app.route("/display")
def display():
    if 'loggedin' in session:
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
            account = cursor.fetchone()
            return render_template("display.html", account=account)
        except Exception as e:
            logger.error(f"Display error: {str(e)}")
            return redirect(url_for('login'))
        finally:
            if 'cursor' in locals():
                cursor.close()
    return redirect(url_for('login'))


@app.route("/update", methods=['GET', 'POST'])
def update():
    msg = ''
    try:
        if 'loggedin' in session:
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                email = request.form['email']
                collage = request.form['collage']
                city = request.form['city']
                state = request.form['state']
                country = request.form['country']
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    'SELECT * FROM accounts WHERE username = % s',
                      (username, ))
                account = cursor.fetchone()
                if account:
                    msg = 'Account already exists !'
                elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    msg = 'Invalid email address !'
                elif not re.match(r'[A-Za-z0-9]+', username):
                    msg = 'name must contain only characters and numbers !'
                else:
                    # Hash the new password
                    hashed_password = generate_password_hash(password)
                    
                    cursor.execute(
                        'UPDATE accounts SET username = %s, '
                        'password = %s, email = %s, collage = %s, '
                        'city = %s, state = %s, '
                        'country = %s WHERE id = %s',
                        (username, hashed_password, email, collage, 
                        city, state, country, session['id'])
                    )
                    mysql.connection.commit()
                    logger.info(f"User {username} updated their profile")
                    msg = 'Profile updated successfully!'
    except Exception as e:
        logger.error(f"Update error: {str(e)}")
        msg = 'An error occurred during update'
    finally:
        if 'cursor' in locals():
            cursor.close()
    
    return render_template("update.html", msg=msg)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)