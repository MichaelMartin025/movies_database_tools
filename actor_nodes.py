import os
import sys
import psycopg
import networkx as nx
import matplotlib.pyplot as plt
from thefuzz import process
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

def get_all_actor_names():
    try:
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT actor_name FROM stars ORDER BY actor_name;")
                return [row[0] for row in cur.fetchall()]
    except psycopg.Error as e:
        print("❌ Failed to fetch actor names:", e)
        return []

def get_collaborators(actor_name):
    try:
        with psycopg.connect(**DB_CONNECTION) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        CASE WHEN s1.actor_name = %s THEN s2.actor_name ELSE s1.actor_name END AS collaborator,
                        STRING_AGG(DISTINCT m.title, ', ') AS movies,
                        COUNT(DISTINCT m.title) AS shared_movies
                    FROM appearances a1
                    JOIN appearances a2 ON a1.movie_id = a2.movie_id AND a1.star_id != a2.star_id
                    JOIN stars s1 ON a1.star_id = s1.id
                    JOIN stars s2 ON a2.star_id = s2.id
                    JOIN movies m ON a1.movie_id = m.id
                    WHERE %s IN (s1.actor_name, s2.actor_name)
                    GROUP BY collaborator
                    ORDER BY shared_movies DESC;
                """, (actor_name, actor_name))
                return cur.fetchall()
    except psycopg.Error as e:
        print("❌ Error fetching collaborators:", e)
        return []

def build_rel_graph(center_actor):
    G = nx.Graph()
    G.add_node(center_actor, layer=0)

    first_degree = get_collaborators(center_actor)
    first_degree_names = set()

    # First-degree edges
    for actor, movies, count in first_degree:
        G.add_node(actor, layer=1)
        G.add_edge(center_actor, actor, weight=count, movies=movies)
        first_degree_names.add(actor)

    # Second-degree
    for actor in first_degree_names:
        second_degree = get_collaborators(actor)
        for coactor, movies, count in second_degree:
            if coactor == center_actor or coactor in first_degree_names:
                continue  # Already in graph or directly connected to center
            G.add_node(coactor, layer=2)
            G.add_edge(actor, coactor, weight=count, movies=movies)

    return G

def draw_graph(G, center_actor):
    pos = nx.spring_layout(G, seed=42, k=1.2)
    layers = nx.get_node_attributes(G, 'layer')

    plt.figure(figsize=(12, 8))

    # Draw nodes with color by layer
    for layer, color in zip((0, 1, 2), ('deepskyblue', 'mediumseagreen', 'lightgray')):
        nodes = [n for n in G.nodes if layers.get(n) == layer]
        nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=color, node_size=500)

    # Edges
    weights = [G[u][v]["weight"] for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, width=[w * 1.3 for w in weights], alpha=0.4, connectionstyle="arc3,rad=0.15", arrows=True)

    # Labels
    nx.draw_networkx_labels(G, pos, font_size=9)

    # Edge labels
    edge_labels = {(u, v): G[u][v]["movies"] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, label_pos=0.5)

    plt.title(f"Actor Collaboration Map: {center_actor}", fontsize=14)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

def main():
    print("🎬 Actor Collaboration Map Explorer")
    print("Type an actor name (or number), press Enter to reuse the last, or 'exit' to quit.\n")

    all_actor_names = get_all_actor_names()
    if not all_actor_names:
        print("No actor data found.")
        return

    # Show sample list
    print("Available actors:")
    for i, name in enumerate(all_actor_names[:20], start=1):
        print(f"  {i:>2}. {name}")
    print("  ...\n")

    last_actor = None

    while True:
        try:
            prompt = "Enter actor name or number"
            if last_actor:
                prompt += f" (or Enter to reuse '{last_actor}')"
            actor_input = input(prompt + ": ").strip()

            if actor_input.lower() in ("exit", "quit"):
                print("Goodbye!")
                break

            if not actor_input and last_actor:
                actor_name = last_actor
            elif actor_input.isdigit():
                index = int(actor_input) - 1
                if 0 <= index < len(all_actor_names):
                    actor_name = all_actor_names[index]
                else:
                    print("Invalid number.")
                    continue
            else:
                actor_name = actor_input
                if actor_name not in all_actor_names:
                    match, score = process.extractOne(actor_name, all_actor_names)
                    if score >= 70:
                        confirm = input(f"Did you mean '{match}'? (Y/n): ").strip().lower()
                        if confirm in ("", "y", "yes", ""):
                            actor_name = match
                        else:
                            print("No actor selected.")
                            continue

            last_actor = actor_name

            print(f"\nBuilding graph for {actor_name}...\n")
            G = build_rel_graph(actor_name)

            print("Graph includes:")
            print(f"  - {len(G.nodes())} actors")
            print(f"  - {len(G.edges())} relationships\n")

            draw_graph(G, actor_name)

        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
