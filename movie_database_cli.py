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

def test_connection_and_list_tables():
    try:
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                print("\n✅ Connection successful!")
                print("PostgreSQL version:", version)

                cur.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE';
                """)
                tables = cur.fetchall()

                if tables:
                    print("\n📋 Tables in the database:")
                    for table in tables:
                        print("  -", table[0])
                else:
                    print("\n⚠️ No tables found in the public schema.")
            return True

    except psycopg.Error as e:
        print("\n❌ Connection failed.")
        print("Error:", e)
        return False

def insert_into_database(movie_title, release_year, star_name):
    try:
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                # Check or insert movie
                cur.execute(
                    "SELECT id FROM movies WHERE title = %s AND release_year = %s",
                    (movie_title, release_year)
                )
                movie = cur.fetchone()
                if movie:
                    movie_id = movie[0]
                    print(f"🎬 Movie '{movie_title}' already exists (ID {movie_id}).")
                else:
                    cur.execute(
                        "INSERT INTO movies (title, release_year) VALUES (%s, %s) RETURNING id",
                        (movie_title, release_year)
                    )
                    movie_id = cur.fetchone()[0]
                    print(f"🎬 Inserted movie '{movie_title}' (ID {movie_id}).")

                # Check or insert star
                cur.execute("SELECT id FROM stars WHERE actor_name = %s", (star_name,))
                star = cur.fetchone()
                if star:
                    star_id = star[0]
                    print(f"⭐ Star '{star_name}' already exists (ID {star_id}).")
                else:
                    cur.execute(
                        "INSERT INTO stars (actor_name) VALUES (%s) RETURNING id",
                        (star_name,)
                    )
                    star_id = cur.fetchone()[0]
                    print(f"⭐ Inserted new star '{star_name}' (ID {star_id}).")

                # Link in appearances
                cur.execute(
                    "SELECT id FROM appearances WHERE movie_id = %s AND star_id = %s",
                    (movie_id, star_id)
                )
                if cur.fetchone():
                    print(f"🔁 Appearance already recorded for '{star_name}' in '{movie_title}'.")
                else:
                    cur.execute(
                        "INSERT INTO appearances (movie_id, star_id) VALUES (%s, %s) RETURNING id",
                        (movie_id, star_id)
                    )
                    appearance_id = cur.fetchone()[0]
                    print(f"🎭 Linked appearance (ID {appearance_id}) of '{star_name}' in '{movie_title}'.")

            conn.commit()

    except psycopg.Error as e:
        print("\n❌ Insert failed.")
        print("Error:", e)
        if 'conn' in locals():
            conn.rollback()
            conn.close()

def add_actors_to_movie(title, actor_list):
    try:
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                # Find movie(s) by title only
                cur.execute(
                    "SELECT id, title, release_year FROM movies WHERE title ILIKE %s",
                    (title,)
                )
                matches = cur.fetchall()

                if not matches:
                    print(f"❌ No movie found with title: {title}")
                    return

                if len(matches) > 1:
                    print(f"\n⚠️ Multiple movies found for '{title}':")
                    for i, (mid, t, y) in enumerate(matches, 1):
                        print(f"  {i}. {t} ({y})")
                    selection = input("Select movie number: ").strip()
                    if not selection.isdigit() or int(selection) not in range(1, len(matches) + 1):
                        print("❌ Invalid selection.")
                        return
                    movie_id, movie_title, movie_year = matches[int(selection) - 1]
                else:
                    movie_id, movie_title, movie_year = matches[0]

                for actor_name in actor_list:
                    actor_name = actor_name.strip()
                    if not actor_name:
                        continue

                    # Check or insert star
                    cur.execute("SELECT id FROM stars WHERE actor_name = %s", (actor_name,))
                    star = cur.fetchone()
                    if star:
                        star_id = star[0]
                        print(f"⭐ Found existing star: {actor_name} (ID {star_id})")
                    else:
                        cur.execute(
                            "INSERT INTO stars (actor_name) VALUES (%s) RETURNING id",
                            (actor_name,)
                        )
                        star_id = cur.fetchone()[0]
                        print(f"🌟 Inserted new star: {actor_name} (ID {star_id})")

                    # Link to movie
                    cur.execute(
                        "SELECT id FROM appearances WHERE movie_id = %s AND star_id = %s",
                        (movie_id, star_id)
                    )
                    if cur.fetchone():
                        print(f"🔁 Already linked: {actor_name} in '{movie_title}'")
                    else:
                        cur.execute(
                            "INSERT INTO appearances (movie_id, star_id) VALUES (%s, %s) RETURNING id",
                            (movie_id, star_id)
                        )
                        new_id = cur.fetchone()[0]
                        print(f"✅ Linked {actor_name} to '{movie_title}' (Appearance ID: {new_id})")

            conn.commit()

    except psycopg.Error as e:
        print("❌ Error during actor linking.")
        print("Error:", e)
        if 'conn' in locals():
            conn.rollback()
            conn.close()

def list_actors_for_movie(title):
    try:
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                # Search by title only
                cur.execute(
                    "SELECT id, title, release_year FROM movies WHERE title ILIKE %s",
                    (title,)
                )
                movies = cur.fetchall()
                if not movies:
                    print(f"❌ No movies found with title: {title}")
                    return

                if len(movies) > 1:
                    print(f"\n⚠️ Multiple movies found for '{title}':")
                    for i, (movie_id, t, y) in enumerate(movies, 1):
                        print(f"  {i}. {t} ({y})")
                    selection = input("Select movie number: ").strip()
                    if not selection.isdigit() or int(selection) not in range(1, len(movies)+1):
                        print("❌ Invalid selection.")
                        return
                    movie_id, selected_title, selected_year = movies[int(selection)-1]
                else:
                    movie_id, selected_title, selected_year = movies[0]

                # Get actors
                cur.execute("""
                    SELECT s.actor_name
                    FROM appearances a
                    JOIN stars s ON a.star_id = s.id
                    WHERE a.movie_id = %s
                    ORDER BY s.actor_name;
                """, (movie_id,))
                actors = cur.fetchall()

                print(f"\n🎞️ Movie: {selected_title} ({selected_year})")
                if actors:
                    print("👥 Actors in this movie:")
                    for actor in actors:
                        print("  -", actor[0])
                else:
                    print("⚠️ No actors recorded for this movie.")

    except psycopg.Error as e:
        print("❌ Error retrieving actor list.")
        print("Error:", e)
        if 'conn' in locals():
            conn.close()

def list_movies_for_actor(actor_name):
    try:
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                # Look up star
                cur.execute("SELECT id FROM stars WHERE actor_name = %s", (actor_name,))
                star = cur.fetchone()
                if not star:
                    print(f"❌ Actor not found: {actor_name}")
                    return

                star_id = star[0]

                # Get all movies they appeared in
                cur.execute("""
                    SELECT m.title, m.release_year
                    FROM appearances a
                    JOIN movies m ON a.movie_id = m.id
                    WHERE a.star_id = %s
                    ORDER BY m.release_year, m.title;
                """, (star_id,))

                movies = cur.fetchall()

                print(f"\n🎭 Actor: {actor_name}")
                if movies:
                    print("🎬 Movies featuring this actor:")
                    for title, year in movies:
                        print(f"  - {title} ({year})")
                else:
                    print("⚠️ No movies recorded for this actor.")
    except psycopg.Error as e:
        print("❌ Error retrieving movie list.")
        print("Error:", e)
        if 'conn' in locals():
            conn.close()

def main_menu():
    while True:
        print("\n🎥 Movie Database Menu")
        print("1. Test connection and list tables")
        print("2. Add a new movie and star")
        print("3. Add one or more actors to an existing movie")
        print("4. View actors for a movie")
        print("5. View movies for an actor")
        print("6. Exit")

        choice = input("Enter your choice (1–5): ").strip()

        if choice == "1":
            test_connection_and_list_tables()

        elif choice == "2":
            movie = input("Movie title: ").strip()
            year = input("Release year: ").strip()
            star = input("Star's name: ").strip()

            if not (movie and year and star):
                print("⚠️ All fields are required. Please try again.")
                continue
            try:
                year = int(year)
                insert_into_database(movie, year, star)
            except ValueError:
                print("⚠️ Release year must be a number. Please try again.")

        elif choice == "3":
            title = input("Movie title: ").strip()
            actors = input("Enter actor names (comma-separated): ").strip()

            if not (title and actors):
                print("⚠️ Both title and actor list are required.")
                continue

            actor_list = [name.strip() for name in actors.split(",")]
            add_actors_to_movie(title, actor_list)

        elif choice == "4":
            title = input("Movie title: ").strip()

            if not (title):
                print("⚠️ Title is required.")
                continue

            list_actors_for_movie(title)
            
        elif choice == "5":
            actor_name = input("Actor's name: ").strip()

            if not actor_name:
                print("⚠️ Actor name is required.")
                continue

            list_movies_for_actor(actor_name)
        
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("⚠️ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main_menu()