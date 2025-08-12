import os
import psycopg
import networkx as nx
import matplotlib.pyplot as plt
import time
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
        conn = psycopg.connect(**DB_CONNECTION)
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

def build_graph(pairs):
    G = nx.Graph()
    
    for actor1, actor2, weight in pairs:
        G.add_edge(actor1, actor2, weight=weight)

    return G

def draw_graph(G):
    #for sd in range(101,201):
        sd=73
        print(f"This is using seed #: {sd}")
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, seed=sd, k=0.5)  # Consistent layout  ok seeds: 8
        edges = G.edges(data=True)

        # Line width based on number of shared movies
        weights = [data['weight'] for _, _, data in edges]

        nx.draw_networkx_nodes(G, pos, node_size=200, node_color='lightblue')
        nx.draw_networkx_edges(G, pos, width=weights, alpha=0.6)
        nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")

        plt.title("Actor Collaboration Network")
        plt.axis("off")
        plt.tight_layout()
        plt.show()
        

def main():
    pairs = fetch_actor_pairs()
    if not pairs:
        print("No data to display.")
        return

    G = build_graph(pairs)
    draw_graph(G)

if __name__ == "__main__":
    main()
