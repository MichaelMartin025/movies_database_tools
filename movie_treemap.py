import os
import psycopg
import pandas as pd
import matplotlib.pyplot as plt
import squarify  # pip install squarify
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


def fetch_movie_actor_counts():
    try:
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT m.title, m.release_year, COUNT(a.star_id) AS actor_count
                    FROM movies m
                    LEFT JOIN appearances a ON m.id = a.movie_id
                    GROUP BY m.id
                    ORDER BY m.release_year, m.title;
                """)
                rows = cur.fetchall()


        df = pd.DataFrame(rows, columns=["title", "release_year", "actor_count"])
        return df

    except psycopg.Error as e:
        print("❌ Failed to fetch movie data.")
        print("Error:", e)
        return pd.DataFrame()

def plot_treemap(df):
    if df.empty:
        print("⚠️ No data to display.")
        return

    # Format labels like: "Titanic (1997)"
    df["label"] = df.apply(lambda row: f"{row['title']} ({row['release_year']})", axis=1)

    # Actor count determines block size
    sizes = df["actor_count"].tolist()
    labels = df["label"].tolist()

    # Optional: hide labels for very small boxes
    display_labels = [
        label if size >= 2 else ""
        for label, size in zip(labels, sizes)
    ]

    plt.figure(figsize=(16, 10))
    squarify.plot(sizes=sizes, label=display_labels, alpha=0.8)
    plt.axis("off")
    plt.title("Movie TreeMap — Size by Number of Actors")
    plt.show()

def main():
    df = fetch_movie_actor_counts()
    plot_treemap(df)

if __name__ == "__main__":
    main()
