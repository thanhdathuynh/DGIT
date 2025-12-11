from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
import MySQLdb

load_dotenv()

mysql = MySQL()

def init_app(app):
    app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
    app.config['MYSQL_USER'] = os.getenv('DB_USER')
    app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD')
    app.config['MYSQL_DB'] = os.getenv('DB_NAME')
    
    mysql.init_app(app)

def create_database():
    host = os.getenv('DB_HOST')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    port = int(os.getenv('DB_PORT', 3306))

    print(f"Connecting to MySQL server at {host}:{port} as {user}...")

    conn = MySQLdb.connect(host=host, user=user, passwd=password, port=port)
    cur = conn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS DGIT")
    cur.execute(f"USE DGIT")
    cur.execute(f"""create table IF NOT EXISTS messages (
                id int auto_increment primary key,
                name varchar(100),
                email varchar(100),
                message text not null,
                time timestamp default current_timestamp)""")
    cur.execute(f"""CREATE TABLE IF NOT EXISTS search_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                drug_name VARCHAR(255) NOT NULL,
                gene_name VARCHAR(255) NOT NULL,
                interaction_type VARCHAR(255),
                confidence_score FLOAT)""")
    conn.commit()
    cur.close()
    conn.close()
