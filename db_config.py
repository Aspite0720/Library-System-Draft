import mysql.connector
from mysql.connector import Error


DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "",           # ← your MySQL password (blank if using XAMPP default)
    "database": "elibrary_db"
}

def get_connection():
    """Returns a live MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)
