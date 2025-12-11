from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
import json
import mysql.connector as mysql_conn
from mysql.connector import Error

load_dotenv()

mysql = MySQL()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def initialize_database():
    try:
        #Connect WITHOUT selecting a database yet
        conn = mysql_conn.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # Create the database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4;")
        print(f"Database `{DB_NAME}` ready.")

        cursor.close()
        conn.close()

        # Connect again, now INTO the created database
        conn = mysql_conn.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_cache (
                id INT AUTO_INCREMENT PRIMARY KEY,
                query VARCHAR(255),
                search_type VARCHAR(50),
                result_json LONGTEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        print("Table `search_cache` ready.")



        cursor.execute(f"""create table IF NOT EXISTS messages (
                id int auto_increment primary key,
                name varchar(100),
                email varchar(100),
                message text not null,
                time timestamp default current_timestamp)""")
        
        print("Table 'messages' ready.")
        
        conn.commit()
        cursor.close()
        conn.close()



    except Exception as e:
        print("Error initializing database:", e)

#Flask config initialization after db exists
def init_app(app):
    initialize_database()

    app.config['MYSQL_HOST'] = DB_HOST
    app.config['MYSQL_USER'] = DB_USER
    app.config['MYSQL_PASSWORD'] = DB_PASSWORD
    app.config['MYSQL_DB'] = DB_NAME

# CACHE SYSTEM FOR SEARCH RESULTS
def get_cached_results(query, search_type):
    """
    Returns cached results from the search_cache table.
    """
    try:
        conn = mysql.connection
        cursor = conn.cursor()

        sql = """
            SELECT result_json
            FROM search_cache
            WHERE query = %s AND search_type = %s
        """

        cursor.execute(sql, (query.lower(), search_type))
        row = cursor.fetchone()

        cursor.close()

        if row:
            # row[0] contains the JSON string
            return json.loads(row[0])

        return None

    except Exception as e:
        print("\n[DB ERROR - get_cached_results]\n", e)
        return None


def save_results(query, search_type, results):
    """
    Saves API results into the search_cache table.
    """
    try:
        conn = mysql.connection
        cursor = conn.cursor()

        sql = """
            INSERT INTO search_cache (query, search_type, result_json)
            VALUES (%s, %s, %s)
        """

        cursor.execute(sql, (
            query.lower(),
            search_type,
            json.dumps(results)
        ))

        conn.commit()
        cursor.close()

    except Exception as e:
        print("\n[DB ERROR - save_results]\n", e)
