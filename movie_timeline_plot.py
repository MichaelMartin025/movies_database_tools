import os
import psycopg
import pandas as pd
import matplotlib.pyplot as plt
import random
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

def fetch_movies():
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
                rows = cur.fetchall()


        df = pd.DataFrame(rows, columns=["title", "release_year", "actor_count"])
        return df

    except psycopg.Error as e:
        print("❌ Failed to fetch movie data.")
        print("Error:", e)
        return pd.DataFrame()

def plot_timeline(df):
    if df.empty:
        print("⚠️ No data to display.")
        return

    # Add slight vertical jitter to separate dots visually
    df["y"] = [random.uniform(-0.2, 0.2) for _ in range(len(df))]

    plt.figure(figsize=(14, 6))
    scatter = plt.scatter(
        df["release_year"],
        df["y"],
        s=df["actor_count"] * 30,  # Bubble size scaled by actor count
        alpha=0.7,
        c=df["actor_count"],
        cmap="viridis",
        edgecolors="black"
    )

    plt.xlabel("Release Year")
    plt.title("Movie Timeline — Each Dot = One Movie (Size = # Actors)")
    plt.yticks([])  # Hide y-axis
    plt.grid(axis="x", linestyle="--", alpha=0.3)

    # Optional: annotate a few selected movies
    for _, row in df.iterrows():
        if row["actor_count"] >= 4:  # only annotate larger movies
            plt.annotate(
                row["title"],
                (row["release_year"], row["y"]),
                textcoords="offset points",
                xytext=(0, 6),
                ha='center',
                fontsize=8
            )

    plt.colorbar(scatter, label="Number of Actors")
    plt.tight_layout()
    plt.show()

def main():
    df = fetch_movies()
    plot_timeline(df)

if __name__ == "__main__":
    main()
