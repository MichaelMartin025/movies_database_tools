import os
import psycopg
import networkx as nx
import matplotlib.pyplot as plt
from operator import itemgetter
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

def build_graph(pairs):
    G = nx.Graph()

    for actor1, actor2, weight in pairs:
        G.add_edge(actor1, actor2, weight=weight)

    return G

def draw_graph(G):
    plt.figure(figsize=(16, 9))  # Larger canvas
    pos = nx.random_layout(G)

    edges = G.edges(data=True)
    weights = [data['weight'] for _, _, data in edges]

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=300, node_color='skyblue')

    # Draw edges with varying thickness and transparency
    nx.draw_networkx_edges(G, pos, width=[w * 0.5 for w in weights], alpha=0.4)

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=9)

    plt.title("Top Actor Collaboration Network", fontsize=20)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

def main():
    pairs = fetch_actor_pairs()
    if not pairs:
        print("No data to display.")
        return

    full_graph = build_graph(pairs)

    # Optional: Limit to top 30 most connected actors for clarity
    top_nodes = sorted(full_graph.degree, key=itemgetter(1), reverse=True)[:30]
    filtered_graph = full_graph.subgraph([node for node, _ in top_nodes])

    draw_graph(filtered_graph)

if __name__ == "__main__":
    main()
