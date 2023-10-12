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
        """
        Establishes a database connection using the provided parameters.
        The connection and cursor will be accessible as 'conn' and 'cursor,' respectively.
        """
        self.conn = mysql.connector.connect(
            host= host,
            user= user,
            password= password,
            database= database
        )
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=None):
        """
        Executes select or insert query.
        Returns the selected data or the row affected count.
        """
        self.cursor.execute(query, params)
        if self.cursor.description is not None: # SELECT query
            return self.cursor.fetchall()
        self.conn.commit()
        return self.cursor.rowcount
        
    def close_connection(self):
        """
        Closes the database connection.
        """
        self.cursor.close()
        self.conn.close()
