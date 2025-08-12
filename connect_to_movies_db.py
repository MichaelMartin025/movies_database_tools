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

def test_connection_and_list_tables():
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
        return True

    except psycopg.Error as e:
        print("Connection failed.")
        print("Error:", e)

def insert_into_database(movie_title, release_year, star_name):

    with psycopg.connect(**DB_CONNECTION) as conn:

        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO movies (title, release_year) VALUES (%s, %s) RETURNING id",
                (movie_title, release_year)
            )

            # Get the ID of the inserted row
            movies_inserted_id = cur.fetchone()[0]
            print("Inserted row ID in movies db:", movies_inserted_id)

            cur.execute(
                "INSERT INTO stars (actor_name) VALUES (%s) RETURNING id",
                (star_name)
            )

            # Get the ID of the inserted row
            stars_inserted_id = cur.fetchone()[0]
            print("Inserted in row ID in stars db:", stars_inserted_id)

    # Commit the transaction
    conn.commit()

if test_connection_and_list_tables():

    ask_to_add = input("Do you want to add to movies database at this time? ")
    if ask_to_add == "yes":
        movie = input("Movie title: ")
        year = input("Release year: ")
        actor = input("Star's name: ")
        insert_into_database(movie, int(year), actor)
