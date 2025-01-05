import psycopg2
from psycopg2 import sql
import os

def create_database(db_name, db_user, db_password, host='localhost', port='8080'):
    """
    Creates a new PostgreSQL database with the specified parameters.

    Args:
        db_name (str): The name of the database to create.
        db_user (str): The user that will own the new database.
        db_password (str): The password for the database user.
        host (str, optional): The host of the PostgreSQL server. Defaults to 'localhost'.
        port (str, optional): The port of the PostgreSQL server. Defaults to '8080'.
    """
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(
            dbname='postgres',
            user=db_user,
            password=db_password,
            host=host,
            port=port
        )
        connection.autocommit = True
        cursor = connection.cursor()

        cursor.execute(sql.SQL("""
            CREATE DATABASE {db_name}
            WITH OWNER = {owner}
            ENCODING = 'UTF8'
            CONNECTION LIMIT = -1;
        """).format(
            db_name=sql.Identifier(db_name),
            owner=sql.Identifier(db_user)
        ))

        print(f"Database '{db_name}' created successfully with owner '{db_user}'.")
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

if __name__ == "__main__":
    DB_NAME = os.getenv('DB_NAME', 'library_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '8000')

    create_database(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)