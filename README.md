[movie_database_python_postgre_sql_readme.md](https://github.com/user-attachments/files/21726336/movie_database_python_postgre_sql_readme.md)
# Movie Database (Python + PostgreSQL)

A small collection of Python scripts I use to track movies I’ve watched and the actors who appear in them. It stores data in PostgreSQL and includes handy queries plus a simple collaborator network visualization.

---

## Features

- **PostgreSQL schema** with three core tables: `movies`, `stars`, and the join table `appearances`.
- **Analysis scripts**:
  - List the **actor with the most appearances**.
  - List **movies that currently have no actors recorded** (data cleanup helper).
  - Build a **co‑appearance map** (which actors have appeared together and how often) and print readable summaries.
- **Visualization**:
  - Optional **NetworkX/Matplotlib** “actor network” (nodes = actors, edges = shared movies). Curved edges optional.
- **Safe configuration** via a local `.env` file (kept out of Git) using `python-dotenv`.

---

## Repo layout (example)

```
movies_database/
├─ actor_nodes.py              # Network graph of actor co‑appearances
├─ collaborators_cli.py        # Prints per‑actor collaborator lists
├─ max_actor.py                # Actor with most appearances
├─ movies_without_actors.py    # Data cleanup report
├─ db/
│  ├─ schema.sql               # Minimal schema to get started
│  └─ sample_data.sql          # (Optional) tiny seed data for testing
├─ .env.example                # Template for local secrets (safe to commit)
├─ requirements.txt            # Python dependencies
└─ README.md                   # This file
```

> File names above match the intent of existing scripts. If yours differ, adjust the examples below.

---

## Prerequisites

- **Python 3.10+** (any recent 3.x is fine)
- **PostgreSQL 14+** (local install is fine)
- **pip** for installing Python packages

### Python packages

```
# requirements.txt
psycopg[binary]>=3.1
python-dotenv>=1.0
networkx>=3.0
matplotlib>=3.7
# pyvis is optional if you want an interactive HTML graph
pyvis>=0.3  # optional
```

Install:

```bash
pip install -r requirements.txt
```

---

## Setup

### 1) Create the database (one‑time)

Create a database named `Movies` (or pick your own name):

```sql
-- in psql
CREATE DATABASE "Movies";
```

### 2) Create tables

A minimal schema (edit as you like) — `db/schema.sql`:

```sql
CREATE TABLE IF NOT EXISTS movies (
  id      SERIAL PRIMARY KEY,
  title   TEXT NOT NULL,
  year    INT
);

CREATE TABLE IF NOT EXISTS stars (
  id          SERIAL PRIMARY KEY,
  actor_name  TEXT NOT NULL
);

-- join table: which actors appeared in which movie
CREATE TABLE IF NOT EXISTS appearances (
  movie_id  INT NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
  star_id   INT NOT NULL REFERENCES stars(id)  ON DELETE CASCADE,
  PRIMARY KEY (movie_id, star_id)
);
```

Apply it:

```bash
psql -U postgres -d Movies -f db/schema.sql
```

> If your PostgreSQL superuser isn’t `postgres`, change the `-U` value.

### 3) Configure environment variables (no secrets in code!)

Copy the template and fill in your local values:

```bash
cp .env.example .env
```

`.env.example`:

```
PGDATABASE=Movies
PGUSER=postgres
PGPASSWORD=
PGHOST=localhost
PGPORT=5432
```

Edit `.env` (do **not** commit it) and set `PGPASSWORD` to your real password. Ensure `.gitignore` contains:

```
.env
```

### 4) (Optional) Seed some test data

Add a couple of movies/actors to try things out — `db/sample_data.sql`:

```sql
INSERT INTO movies (title, year) VALUES
  ('Heat', 1995),
  ('Ocean''s Eleven', 2001);

INSERT INTO stars (actor_name) VALUES
  ('Al Pacino'),
  ('Robert De Niro'),
  ('George Clooney'),
  ('Brad Pitt');

INSERT INTO appearances (movie_id, star_id) VALUES
  ((SELECT id FROM movies WHERE title='Heat'), (SELECT id FROM stars WHERE actor_name='Al Pacino')),
  ((SELECT id FROM movies WHERE title='Heat'), (SELECT id FROM stars WHERE actor_name='Robert De Niro')),
  ((SELECT id FROM movies WHERE title='Ocean''s Eleven'), (SELECT id FROM stars WHERE actor_name='George Clooney')),
  ((SELECT id FROM movies WHERE title='Ocean''s Eleven'), (SELECT id FROM stars WHERE actor_name='Brad Pitt'));
```

Apply it:

```bash
psql -U postgres -d Movies -f db/sample_data.sql
```

---

## How the scripts read the `.env`

Example pattern used by the Python files:

```python
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()  # reads .env sitting next to your scripts

DB_PARAMS = {
    "dbname": os.getenv("PGDATABASE", "Movies"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", ""),
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5432"),
}

with psycopg.connect(**DB_PARAMS) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT 1;")
        print("DB connection OK")
```

---

## Usage

### Actor with most appearances

```bash
python max_actor.py
```

Sample output:

```
🏆 Actor with most appearances: Robert De Niro (17 movies)
```

### Movies without any actors (data cleanup)

```bash
python movies_without_actors.py
```

Sample output:

```
⚠️ Movies lacking actor entries:
- <title> (<year>)
```

### Print collaborator lists (who co‑stars with whom)

```bash
python collaborators_cli.py
```

Sample output:

```
Actor: Al Pacino
  - Robert De Niro (3)

Actor: Brad Pitt
  - George Clooney (4)
```

### Visualize the actor network (NetworkX)

```bash
python actor_nodes.py
```

Tips:

- If you see a warning about `connectionstyle` and `LineCollection`, either remove the `connectionstyle` option **or** run with `arrows=True` to force curved edges via FancyArrowPatches (might be slower for very large graphs).
- Example edit inside `actor_nodes.py`:

```python
nx.draw_networkx_edges(
    G, pos,
    width=[w * 1.3 for w in weights],
    alpha=0.4,
    # connectionstyle="arc3,rad=0.15",
    # arrows=True,
)
```

---

## Security notes

- **Do not commit real credentials.** Use `.env` locally and keep it out of Git.
- Commit a safe `` so others know which variables to set.
- If a secret was ever committed, **change/rotate it**, then consider rewriting Git history with `git filter-repo` or BFG before force‑pushing.

---

## Troubleshooting

- ``
  - Check `.env` values (DB name, user, password, host, port).
  - Confirm the DB is running and you can `psql -U postgres -d Movies`.
- **Windows local auth**
  - You can configure SSPI/Integrated auth in `pg_hba.conf` to avoid passwords for local use.
- **Matplotlib window doesn’t show**
  - On some systems you may need `python -m pip install matplotlib` and ensure a GUI backend is available. Alternatively, save figures to files.
- **Network graph is slow on big data**
  - Hide labels for large graphs, reduce edge count (filter low weights), or skip `arrows=True`.

---

## License

This project is licensed under the MIT License — you are free to use, modify, and distribute it with attribution. See the LICENSE file for details.

---

## Roadmap / Nice‑to‑haves

- CLI flags for output formats (table/CSV/JSON).
- Optional interactive HTML graph via **PyVis**.
- Caching and fuzzy matching for actor lookups.
- Tkinter GUI for browsing towns—err, movies 😉 (future experiment).

---

## Acknowledgments

Built for personal tracking and learning; thanks to PostgreSQL, psycopg, NetworkX, and Matplotlib communities.

