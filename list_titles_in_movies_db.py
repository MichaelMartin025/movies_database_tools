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

def list_all_titles_in_movies(sort):

    with psycopg.connect(**DB_CONNECTION) as conn:

        with conn.cursor() as cur:

            if sort == "name":
                cur.execute("SELECT * FROM movies ORDER BY title")
            elif sort == "year":
                cur.execute("SELECT * FROM movies ORDER BY release_year")
            else:
                cur.execute("SELECT * FROM movies")
                
            all_titles = cur.fetchall()

            for title in all_titles:
                print("-", title[0], title[1], title[2])



print("List all titles in movies database.")
sort_method = input("Choose a sort method (name, year, none): ")
list_all_titles_in_movies(sort_method)