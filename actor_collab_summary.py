import os
import psycopg
from collections import defaultdict
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

def fetch_actor_pairs():
    try:
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        s1.actor_name AS actor_1,
                        s2.actor_name AS actor_2,
                        COUNT(*) AS shared_movies
                    FROM appearances a1
                    JOIN appearances a2
                        ON a1.movie_id = a2.movie_id AND a1.star_id < a2.star_id
                    JOIN stars s1 ON a1.star_id = s1.id
                    JOIN stars s2 ON a2.star_id = s2.id
                    GROUP BY s1.actor_name, s2.actor_name
                    HAVING COUNT(*) > 0
                    ORDER BY shared_movies DESC;
                """)
                return cur.fetchall()
    except psycopg.Error as e:
        print("❌ Database query failed.")
        print("Error:", e)
        return []

def build_collaborator_map(pairs):
    collaborators = defaultdict(list)

    for actor1, actor2, count in pairs:
        collaborators[actor1].append((actor2, count))
        collaborators[actor2].append((actor1, count))  # Symmetric

    return collaborators

def display_collaborators(collaborators):
    for actor in sorted(collaborators):
        print(f"\nActor: {actor}")
        # Sort by most frequent co-stars
        sorted_collabs = sorted(collaborators[actor], key=lambda x: -x[1])
        for coactor, count in sorted_collabs:
            print(f"  - {coactor} ({count})")

def main():
    pairs = fetch_actor_pairs()
    if not pairs:
        print("No collaboration data found.")
        return

    collaborators = build_collaborator_map(pairs)
    display_collaborators(collaborators)

if __name__ == "__main__":
    main()
