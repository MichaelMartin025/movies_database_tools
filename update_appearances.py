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

existing_appearances = {
    ("Titanic", 1997): ["Kate Winslet", "Leonardo DiCaprio"],
    ("Juno", 2007): ["Elliot Page", "Michael Cera"],
    ("Blended", 2014): ["Drew Barrymore"],
    ("The Bounty Hunter", 2010): [],  # No actors (yet)
}

def add_bulk_appearances(data):
    try:
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                for (title, year), actor_list in data.items():
                    # Skip if no actors to add
                    if not actor_list:
                        print(f"🕊️ Skipping '{title}' ({year}) — no actors listed.")
                        continue

                    # Get movie ID
                    cur.execute(
                        "SELECT id FROM movies WHERE title = %s AND release_year = %s",
                        (title, year)
                    )
                    movie = cur.fetchone()
                    if not movie:
                        print(f"⚠️ Movie not found: {title} ({year})")
                        continue
                    movie_id = movie[0]

                    for actor in actor_list:
                        # Get star ID
                        cur.execute(
                            "SELECT id FROM stars WHERE actor_name = %s",
                            (actor,)
                        )
                        star = cur.fetchone()
                        if not star:
                            print(f"⚠️ Star not found: {actor}")
                            continue
                        star_id = star[0]

                        # Check and insert into appearances
                        cur.execute(
                            "SELECT id FROM appearances WHERE movie_id = %s AND star_id = %s",
                            (movie_id, star_id)
                        )
                        if cur.fetchone():
                            print(f"🔁 Appearance already exists: {actor} in '{title}'")
                        else:
                            cur.execute(
                                "INSERT INTO appearances (movie_id, star_id) VALUES (%s, %s) RETURNING id",
                                (movie_id, star_id)
                            )
                            new_id = cur.fetchone()[0]
                            print(f"✅ Linked {actor} to '{title}' (ID: {new_id})")

            conn.commit()


    except psycopg.Error as e:
        print("❌ Error during linking.")
        print("Error:", e)
        if 'conn' in locals():
            conn.rollback()
            conn.close()

# Run it
add_bulk_appearances(existing_appearances)
