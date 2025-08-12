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

def actor_with_most_appearances():
    try:
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT s.actor_name, COUNT(*) AS appearance_count
                    FROM stars s
                    JOIN appearances a ON s.id = a.star_id
                    GROUP BY s.actor_name
                    ORDER BY appearance_count DESC
                    LIMIT 1;
                """)
                result = cur.fetchone()
                if result:
                    print(f"\n🏆 Actor with most appearances: {result[0]} ({result[1]} movies)")
                else:
                    print("⚠️ No appearances found.")
    except psycopg.Error as e:
        print("❌ Query failed.")
        print("Error:", e)

def movies_without_actors():
    try:
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT m.title, m.release_year
                    FROM movies m
                    LEFT JOIN appearances a ON m.id = a.movie_id
                    WHERE a.movie_id IS NULL
                    ORDER BY m.release_year, m.title;
                """)
                results = cur.fetchall()
                print("\n📋 Movies without any recorded actors:")
                if results:
                    for title, year in results:
                        print(f"  - {title} ({year})")
                else:
                    print("✅ All movies have at least one actor listed.")
    except psycopg.Error as e:
        print("❌ Query failed.")
        print("Error:", e)

def actors_without_movies():
    try:
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT s.actor_name
                    FROM stars s
                    LEFT JOIN appearances a ON s.id = a.star_id
                    WHERE a.star_id IS NULL
                    ORDER BY s.actor_name;
                """)
                results = cur.fetchall()
                print("\n🧍 Actors not linked to any movies:")
                if results:
                    for (name,) in results:
                        print(f"  - {name}")
                else:
                    print("✅ All actors are linked to at least one movie.")
    except psycopg.Error as e:
        print("❌ Query failed.")
        print("Error:", e)

def actor_pairs_by_shared_movies():
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
                    GROUP BY actor_1, actor_2
                    HAVING COUNT(*) > 0
                    ORDER BY shared_movies DESC, actor_1, actor_2;
                """)
                results = cur.fetchall()
                print("\n🤝 Actor pairs who have worked together:")
                if results:
                    for actor1, actor2, count in results:
                        print(f"  - {actor1} & {actor2} — {count} movie(s)")
                else:
                    print("⚠️ No actor pairs found.")
    except psycopg.Error as e:
        print("❌ Query failed.")
        print("Error:", e)

def list_movies_with_one_actor():
    try:
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT m.id, m.title, m.release_year
                    FROM movies m
                    JOIN appearances a ON m.id = a.movie_id
                    GROUP BY m.id, m.title, m.release_year
                    HAVING COUNT(a.star_id) = 1
                    ORDER BY m.title;
                """)
                return cur.fetchall()
    except psycopg.Error as e:
        print("❌ Query failed when fetching movies with one actor.")
        print("Error:", e)
        return []

def add_actors_to_movie(movie_id, movie_title):
    print(f"\n➕ Adding actors to '{movie_title}' (Movie ID: {movie_id})")
    while True:
        actor_name = input("Enter actor name (or press Enter to finish): ").strip()
        if not actor_name:
            break
        try:
            with psycopg.connect(DB_CONNECTION) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM stars WHERE actor_name = %s;", (actor_name,))
                    result = cur.fetchone()
                    if result:
                        actor_id = result[0]
                    else:
                        cur.execute("INSERT INTO stars (actor_name) VALUES (%s) RETURNING id;", (actor_name,))
                        actor_id = cur.fetchone()[0]
                    cur.execute("""
                        INSERT INTO appearances (movie_id, star_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (movie_id, actor_id))
                    print(f"✅ Added {actor_name}")
        except psycopg.Error as e:
            print("❌ Error adding actor.")
            print("Error:", e)

def main_menu():
    while True:
        print("\n🎞️ Movie Stats Menu")
        print("1. Show actor with most appearances")
        print("2. List movies with no actors recorded")
        print("3. List actors with no movies recorded")
        print("4. List all actor pairs who have worked together")
        print("5. List movies with one actor and add more")
        print("6. Exit")

        choice = input("Choose an option (1–6): ").strip()

        if choice == "1":
            actor_with_most_appearances()
        elif choice == "2":
            movies_without_actors()
        elif choice == "3":
            actors_without_movies()
        elif choice == "4":
            actor_pairs_by_shared_movies()
        elif choice == "5":
            movies = list_movies_with_one_actor()
            if not movies:
                print("🎬 All movies have more than one actor.")
                continue

            print("\n📋 Movies with only one actor:")
            for i, (movie_id, title, year) in enumerate(movies, start=1):
                print(f"  {i}. {title} ({year})")

            selection = input("Select a movie by number: ").strip()
            if not selection.isdigit() or not (1 <= int(selection) <= len(movies)):
                print("⚠️ Invalid selection.")
                continue

            selected_movie = movies[int(selection) - 1]
            add_actors_to_movie(selected_movie[0], selected_movie[1])
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("⚠️ Invalid choice. Please enter a number from 1 to 6.")

if __name__ == "__main__":
    main_menu()
