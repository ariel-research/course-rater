import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self,
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")):
        self.conn = mysql.connector.connect(
            host= host,
            user= user,
            password= password,
            database= database
        )
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params)
        if self.cursor.description is not None: # SELECT query
            return self.cursor.fetchall()
        self.conn.commit()
        return self.cursor.rowcount
        

    # Other methods for different database operations

    def close_connection(self):
        self.cursor.close()
        self.conn.close()
