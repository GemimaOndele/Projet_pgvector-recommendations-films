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
    # Nom du dataset Hugging Face (à adapter, par ex. "auteur/mon-dataset-films")
    dataset_name = os.environ.get("HF_DATASET_NAME", "A_COMPLETER")

    if dataset_name == "A_COMPLETER":
        raise ValueError(
            "Merci de définir la variable d'environnement HF_DATASET_NAME "
            "avec le nom complet du dataset Hugging Face (ex: auteur/mon-dataset-films)."
        )

    # Le token doit être passé via la variable d'environnement HF_TOKEN si nécessaire.
    # La librairie `datasets` lira automatiquement ce token.
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token

    print(f"Téléchargement du dataset Hugging Face : {dataset_name}")
    ds = load_dataset(dataset_name, split="train")
    df = ds.to_pandas()

    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "films.csv")
    df.to_csv(output_path, index=False)

    print(f"Dataset sauvegardé au format CSV dans : {output_path}")


if __name__ == "__main__":
    main()


