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

def search_for_stars(name):

    with psycopg.connect(**DB_CONNECTION) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM stars WHERE actor_name =%s", (name,))
            star_data = cur.fetchall()

            if star_data:
                print("Number of names:", len(star_data))

                for row in star_data:
                    print("-", row[1])

            else:
                print(name, "not found in list.")

search_for_stars("Ellie Kemper")