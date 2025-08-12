import os
import psycopg
from dotenv import load_dotenv

# Load values from .env file
load_dotenv()

DB_CONNECTION = {
    "dbname": os.getenv("PGDATABASE", "Movies"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", ""),
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5432"),
}

try:
    # Connect to the database
    with psycopg.connect(**DB_CONNECTION) as conn:
        with conn.cursor() as cur:
            # Run quick test query
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print("Connection successful!")
            print("PostgreSQL version:", version)

            # List tables
            cur.execute("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_type = 'BASE TABLE';
                        """)
            
            tables = cur.fetchall()
            print("Tables in the database:")
            for table in tables:
                print("-", table[0])

except psycopg.Error as e:
    print("Connection failed.")
    print("Error:", e)
