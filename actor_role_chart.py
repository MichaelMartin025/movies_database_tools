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

def plot_actor_appearance_counts():
    try:
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                # Query actor appearance counts
                cur.execute("""
                    SELECT s.actor_name, COUNT(a.movie_id) AS role_count
                    FROM stars s
                    JOIN appearances a ON s.id = a.star_id
                    GROUP BY s.actor_name
                    ORDER BY role_count DESC;
                """)
                data = cur.fetchall()

        # Convert to DataFrame
        df = pd.DataFrame(data, columns=["Actor", "Roles"])

        # Plot horizontal bar chart
        plt.figure(figsize=(9, max(4, len(df) * 0.2)))
        plt.barh(df["Actor"], df["Roles"], color="mediumseagreen", edgecolor="black")
        plt.xlabel("Number of Roles")
        plt.ylabel("Actor")
        plt.title("Actor Role Count")
        plt.gca().invert_yaxis()  # Highest role count at the top
        plt.grid(axis="x", linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.show()

    except psycopg.Error as e:
        print("❌ Failed to fetch or plot actor data.")
        print("Error:", e)

if __name__ == "__main__":
    plot_actor_appearance_counts()
