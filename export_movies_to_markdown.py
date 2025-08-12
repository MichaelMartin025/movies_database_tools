import os
import psycopg
import pandas as pd
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

def export_movies_to_markdown(filename="movies_export.md"):
    try:
        # Connect to the database
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                # Fetch movie title, year, and number of actors
                cur.execute("""
                    SELECT m.title, m.release_year, COUNT(a.star_id) AS actor_count
                    FROM movies m
                    LEFT JOIN appearances a ON m.id = a.movie_id
                    GROUP BY m.id
                    ORDER BY m.release_year, m.title;
                """)
                rows = cur.fetchall()
        
        # Build dataframe
        df = pd.DataFrame(rows, columns=["Title", "Year", "# Actors"])

        # Write to markdown
        with open(filename, "w", encoding="utf-8") as f:
            f.write(df.to_markdown(index=False))

        print(f"\n✅ Markdown export saved to: {filename}")

    except psycopg.Error as e:
        print("❌ Database query failed.")
        print("Error:", e)
    except Exception as e:
        print("❌ Export failed.")
        print("Error:", e)

if __name__ == "__main__":
    export_movies_to_markdown()
