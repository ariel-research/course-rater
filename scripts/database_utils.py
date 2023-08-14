import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host= os.getenv("DB_HOST"),
            user= os.getenv("DB_USER"),
            password= os.getenv("DB_PASSWORD"),
            database= os.getenv("DB_NAME"),
        )
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    # Other methods for different database operations

    def close_connection(self):
        self.cursor.close()
        self.conn.close()
