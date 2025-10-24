"""
Create the echobank database if it doesn't exist
Run this before init_db.py
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    """Create echobank database if it doesn't exist"""

    # Connection parameters for default postgres database
    conn_params = {
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": "Timi1997april11",
        "database": "postgres"  # Connect to default database first
    }

    try:
        # Connect to default postgres database
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if echobank database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='echobank'")
        exists = cursor.fetchone()

        if exists:
            print("Database 'echobank' already exists!")
        else:
            # Create echobank database
            print("Creating database 'echobank'...")
            cursor.execute("CREATE DATABASE echobank")
            print("Database 'echobank' created successfully!")

        cursor.close()
        conn.close()
        return True

    except psycopg2.Error as e:
        print(f"Error creating database: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("EchoBank Database Creation")
    print("=" * 50)

    if create_database():
        print("\nSuccess! You can now run init_db.py to create tables and seed data.")
    else:
        print("\nFailed to create database. Please check your PostgreSQL connection.")
