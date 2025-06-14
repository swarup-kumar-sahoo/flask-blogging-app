import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'your_database_name')
}

# Flask Configuration
class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')
    DEBUG = False
    MYSQL_HOST = DB_CONFIG['host']
    MYSQL_USER = DB_CONFIG['user']
    MYSQL_PASSWORD = DB_CONFIG['password']
    MYSQL_DB = DB_CONFIG['database']