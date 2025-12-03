import os

import pandas as pd
from datasets import load_dataset


"""
Script pour télécharger un dataset de films depuis Hugging Face
et le convertir en CSV afin de l'utiliser pour l'ingestion PostgreSQL.

IMPORTANT :
- Ne JAMAIS mettre ton token Hugging Face en dur dans le code.
- Avant de lancer le script, définir la variable d'environnement HF_TOKEN, par exemple :

  export HF_TOKEN="TON_TOKEN_ICI"

Le script utilise ensuite ce token pour accéder à un dataset privé si nécessaire.
"""


def main() -> None:
    # Nom du dataset Hugging Face pour ce projet
    # Dataset public : https://huggingface.co/datasets/Gkop/moviemood-dataset
    dataset_name = os.environ.get("HF_DATASET_NAME", "Gkop/moviemood-dataset")

    # Le token doit être passé via la variable d'environnement HF_TOKEN si nécessaire.
    # La librairie `datasets` lira automatiquement ce token.
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token

    print(f"Téléchargement du dataset Hugging Face : {dataset_name}")
    ds = load_dataset(dataset_name, split="train")
    df = ds.to_pandas()

    # On sélectionne et renomme quelques colonnes pertinentes pour le projet
    # Colonnes disponibles (voir la page du dataset) :
    # - title, genres, main_genre, overview_fr, release_year, etc.
    films_df = pd.DataFrame()
    films_df["title"] = df.get("title")
    films_df["year"] = df.get("release_year")
    films_df["genres"] = df.get("genres")
    # Pas de colonne "cast" dans ce dataset : on laisse vide pour le moment
    films_df["cast"] = ""
    films_df["synopsis"] = df.get("overview_fr")  # synopsis en français

    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "films.csv")
    films_df.to_csv(output_path, index=False)

    print(f"Dataset sauvegardé au format CSV dans : {output_path}")


if __name__ == "__main__":
    main()

