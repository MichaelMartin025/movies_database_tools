import os
import psycopg
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
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


def five_year_box_visual_colored():
    try:
        # Fetch movies
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT title, release_year FROM movies ORDER BY release_year;")
                movies = cur.fetchall()

        # Prepare DataFrame
        df = pd.DataFrame(movies, columns=["Title", "Year"])
        df["IntervalStart"] = (df["Year"] // 5) * 5
        df["Label"] = df["IntervalStart"].astype(str) + "–" + (df["IntervalStart"] + 4).astype(str)

        grouped = df.groupby("Label")
        intervals = sorted(grouped.groups.keys(), key=lambda x: int(x.split("–")[0]))
        num_intervals = len(intervals)

        # Choose a color palette (soft pastel tones)
        colors = ["#f0f8ff", "#e6ffe6", "#fff0f5", "#ffffe0", "#f5f5dc", "#e0ffff"]

        # Layout
        cols = 3
        rows = math.ceil(num_intervals / cols)
        fig, axes = plt.subplots(rows, cols, figsize=(16, rows * 4))
        axes = axes.flatten()

        for idx, label in enumerate(intervals):
            ax = axes[idx]
            group_df = grouped.get_group(label)

            color = colors[idx % len(colors)]
            ax.set_facecolor(color)

            # Draw a filled rectangle behind the text (forces color rendering)
            background = patches.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                                        facecolor=color, edgecolor='none', zorder=0)
            ax.add_patch(background)

            movie_lines = [f"{row['Title']} ({row['Year']})" for _, row in group_df.iterrows()]
            text = "\n".join(movie_lines)
            ax.text(0.01, 0.98, text, va='top', ha='left', fontsize=10, family="monospace", zorder=1)

            ax.set_title(label, fontsize=12, weight="bold")
            ax.axis("off")

            # Draw visible border box
            border = patches.Rectangle((0, 0), 1, 1, linewidth=2.0, edgecolor='gray', facecolor='none',
                                    transform=ax.transAxes, clip_on=False, zorder=2)
            ax.add_patch(border)


        # Hide extras
        for j in range(idx + 1, len(axes)):
            axes[j].axis("off")

        plt.suptitle("Movies Grouped by 5-Year Intervals", fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()

    except psycopg.Error as e:
        print("❌ Database error.")
        print("Error:", e)

if __name__ == "__main__":
    five_year_box_visual_colored()

