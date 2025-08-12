import os
import pandas as pd
import psycopg
from tabulate import tabulate
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


def list_movies_as_table():
    try:
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT m.title, m.release_year, COUNT(a.star_id) AS actor_count
                    FROM movies m
                    LEFT JOIN appearances a ON m.id = a.movie_id
                    GROUP BY m.id
                    ORDER BY m.release_year;
                """)
                data = cur.fetchall()
       
        df = pd.DataFrame(data, columns=["Title", "Year", "# Actors"])

        print("\n🎬 Your Movie List:\n")
        print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))

    except psycopg.Error as e:
        print("❌ Failed to fetch movie list.")
        print("Error:", e)

if __name__ == "__main__":

    list_movies_as_table()
    input("\n📎 Press Enter to close...")

