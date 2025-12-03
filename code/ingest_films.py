"""
Script d'ingestion des films dans PostgreSQL.

Ce script lit le fichier CSV généré par download_dataset.py et insère
les données dans la table 'films' de PostgreSQL.

IMPORTANT :
- Les identifiants PostgreSQL (user, password, host, dbname) doivent être
  passés via des variables d'environnement ou un fichier .env (non versionné).
- Ne JAMAIS commiter les identifiants dans le code.
"""

import os
import sys
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def get_db_connection():
    """
    Crée une connexion PostgreSQL à partir des variables d'environnement.

    Variables attendues :
    - DB_HOST (défaut: localhost)
    - DB_PORT (défaut: 5432)
    - DB_NAME (défaut: filmsrec)
    - DB_USER (requis)
    - DB_PASSWORD (requis)
    """
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    dbname = os.environ.get("DB_NAME", "filmsrec")
    user = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASSWORD")

    if not user or not password:
        raise ValueError(
            "Les variables d'environnement DB_USER et DB_PASSWORD sont requises.\n"
            "Exemple : export DB_USER=postgres && export DB_PASSWORD=ton_mot_de_passe"
        )

    return psycopg2.connect(
        host=host, port=port, dbname=dbname, user=user, password=password
    )


def clean_genres(genres_str):
    """
    Nettoie et convertit une chaîne de genres en liste.

    Exemples d'entrées :
    - "['Action', 'Adventure']" (string Python)
    - "Action|Adventure" (séparé par |)
    - ["Action", "Adventure"] (déjà une liste)
    """
    if pd.isna(genres_str) or not genres_str:
        return []

    # Si c'est déjà une liste
    if isinstance(genres_str, list):
        return [g.strip() for g in genres_str if g and str(g).strip()]

    # Si c'est une string qui ressemble à une liste Python
    if isinstance(genres_str, str):
        # Enlever les crochets et guillemets
        cleaned = genres_str.strip()
        if cleaned.startswith("[") and cleaned.endswith("]"):
            cleaned = cleaned[1:-1]
        # Séparer par virgule ou pipe
        if "|" in cleaned:
            return [g.strip().strip("'\"") for g in cleaned.split("|") if g.strip()]
        elif "," in cleaned:
            return [g.strip().strip("'\"") for g in cleaned.split(",") if g.strip()]

    return []


def ingest_films(csv_path: str = "data/films.csv"):
    """
    Ingère les films depuis un CSV vers PostgreSQL.

    Args:
        csv_path: Chemin vers le fichier CSV contenant les films.
    """
    csv_file = Path(csv_path)
    if not csv_file.exists():
        raise FileNotFoundError(
            f"Le fichier CSV '{csv_path}' n'existe pas.\n"
            "Exécutez d'abord : python code/download_dataset.py"
        )

    print(f"Lecture du fichier CSV : {csv_path}")
    df = pd.read_csv(csv_path)

    # Vérifier les colonnes attendues
    required_cols = ["title", "year", "genres", "cast", "synopsis"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Colonnes manquantes dans le CSV : {missing_cols}\n"
            f"Colonnes disponibles : {list(df.columns)}"
        )

    print(f"Nombre de films à ingérer : {len(df)}")

    conn = get_db_connection()
    cur = conn.cursor()

    # Préparer les données pour insertion
    rows = []
    for _, row in df.iterrows():
        title = str(row["title"]).strip() if pd.notna(row["title"]) else None
        if not title:
            continue  # Ignorer les lignes sans titre

        year = int(row["year"]) if pd.notna(row["year"]) else None
        genres = clean_genres(row["genres"])
        cast = clean_genres(row["cast"]) if pd.notna(row["cast"]) else []
        synopsis = str(row["synopsis"]).strip() if pd.notna(row["synopsis"]) else None

        rows.append((title, year, genres, cast, synopsis, None))  # meta = None pour l'instant

    print(f"Préparation de {len(rows)} films pour insertion...")

    # Insertion en batch avec gestion des doublons (title + year)
    execute_values(
        cur,
        """
        INSERT INTO films (title, year, genres, cast, synopsis, meta)
        VALUES %s
        ON CONFLICT DO NOTHING
        """,
        rows,
        template=None,
        page_size=100,
    )

    inserted = cur.rowcount
    conn.commit()

    print(f"✅ {inserted} films insérés dans la table 'films'.")

    # Afficher un échantillon
    cur.execute("SELECT COUNT(*) FROM films")
    total = cur.fetchone()[0]
    print(f"Total de films dans la base : {total}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingérer des films depuis CSV vers PostgreSQL")
    parser.add_argument(
        "--csv",
        type=str,
        default="data/films.csv",
        help="Chemin vers le fichier CSV (défaut: data/films.csv)",
    )
    args = parser.parse_args()

    try:
        ingest_films(args.csv)
    except Exception as e:
        print(f"❌ Erreur : {e}", file=sys.stderr)
        sys.exit(1)

