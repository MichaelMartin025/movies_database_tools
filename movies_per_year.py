import os
import psycopg
import pandas as pd
import matplotlib.pyplot as plt
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

def plot_movies_per_year_with_total():
    try:
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT release_year FROM movies;")
                years = [row[0] for row in cur.fetchall()]

        df = pd.DataFrame(years, columns=["year"])
        total_movies = len(df)

        # Ensure all years are represented, even with 0 movies
        full_years = pd.Series(range(df["year"].min(), df["year"].max() + 1))
        year_counts = df["year"].value_counts().reindex(full_years, fill_value=0)

        # Plot
        plt.figure(figsize=(10, 6))
        plt.bar(year_counts.index, year_counts.values, color="skyblue", edgecolor="black")
        plt.title(f"Movies Per Year (Total: {total_movies})")
        plt.xlabel("Year")
        plt.ylabel("Number of Movies")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.show()

    except psycopg.Error as e:
        print("❌ Failed to fetch or plot data.")
        print("Error:", e)

if __name__ == "__main__":
    plot_movies_per_year_with_total()