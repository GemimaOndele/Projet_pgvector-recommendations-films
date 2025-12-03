## Projet de recommandation de films avec PostgreSQL + pgvector

Ce projet met en place un **système de recommandation de films** basé sur des **embeddings vectoriels** stockés dans PostgreSQL grâce à l’extension **pgvector**.  
Il couvre toute la chaîne : installation, ingestion de données, génération des embeddings, indexation HNSW, requêtes de similarité, évaluation et petite API de démonstration.

### Objectifs et périmètre

- **Objectif principal** : recommander des films similaires via **recherche sémantique** sur embeddings à partir du **synopsis**, du **cast**, des **genres** et des **métadonnées**.
- **Résultat attendu** :
  - Une base PostgreSQL `filmsrec` avec l’extension `pgvector` activée.
  - Un schéma comprenant les tables `films` et `film_embeddings` (type `vector(768)`).
  - Des scripts d’**ingestion** (CSV / Hugging Face → PostgreSQL) et d’**embeddings** (Sentence Transformers).
  - Un index **HNSW** pour les recherches de similarité rapides.
  - Des **requêtes SQL** de recommandation (films similaires, recherche texte, filtres par genre/année).
  - Une petite **API FastAPI** de démonstration.
  - Une **évaluation de la pertinence** (Precision@K, nDCG, A/B tests simples).

> Pour tous les détails d’**installation** (PostgreSQL, pgvector, Python, création de la base), voir le guide `INSTALLATION.md` à la racine du projet.

---

## Organisation de l’équipe et rôles

- **Rôle 1 — Données et ingestion (Gémima ONDELE)**  
  - Collecte du dataset de films (depuis Hugging Face).  
  - Nettoyage / préparation des données.  
  - Création de la table `films` dans PostgreSQL.  
  - Script Python d’ingestion des données dans la base.

- **Rôle 2 — Embeddings et indexation**  
  - Choix du modèle d’embeddings (ex. `sentence-transformers/all-mpnet-base-v2`).  
  - Génération des embeddings pour chaque film.  
  - Création de la table `film_embeddings` et de l’index HNSW pgvector.  
  - Tuning des paramètres (latence / précision).

- **Rôle 3 — API et intégration (Fatoumata BAH)**  
  - Développement de l’API FastAPI (endpoints de recommandation et recherche).  
  - Connexion à PostgreSQL, écriture des requêtes SQL.  
  - Tests unitaires de l’API.  

- **Rôle 4 — Évaluation et rapport (Hadrien LENON, Hector Benthé KAMBOU)**  
  - Définition du protocole d’évaluation (jeu de requêtes, critères de pertinence).  
  - Calcul des métriques (precision@k, nDCG, etc.).  
  - A/B testing (variantes de champs pris en compte dans les embeddings).  
  - Rédaction du rapport final et préparation de la présentation.

---

## Dataset Hugging Face

- **Source des données** : un dataset de films hébergé sur **Hugging Face** (public ou privé).  
- **Objectif** : répliquer localement les données utilisées pour la recommandation, puis les ingérer dans PostgreSQL.

> ⚠️ **Important sécurité :** le token Hugging Face **ne doit jamais être publié dans GitHub** (ni dans le code, ni dans le README).  
> Utiliser à la place des variables d’environnement (fichier `.env` ignoré par git, par exemple).

### Exemple d’utilisation du dataset (schéma général)

1. Installer la bibliothèque `datasets` ou `huggingface_hub` :

```bash
pip install datasets huggingface_hub
```

2. Dans un script Python (ex. `download_dataset.py`), on peut télécharger et convertir en CSV :

```python
from datasets import load_dataset
import pandas as pd
import os

# Le nom du dataset Hugging Face (à adapter, ex: "auteur/mon-dataset-films")
DATASET_NAME = "A_COMPLETER"

ds = load_dataset(DATASET_NAME, split="train")
df = ds.to_pandas()

# Sauvegarde en CSV pour ingestion dans PostgreSQL
os.makedirs("data", exist_ok=True)
df.to_csv("data/films.csv", index=False)
```

3. Le fichier `data/films.csv` sera ensuite utilisé par le script d’ingestion (Rôle 1).

---

## Cloner et synchroniser le projet avec GitHub

Le dépôt distant GitHub est :  
`https://github.com/GemimaOndele/Projet_pgvector-recommendations-films.git`

### Clonage (sur une nouvelle machine)

```bash
git clone https://github.com/GemimaOndele/Projet_pgvector-recommendations-films.git
cd Projet_pgvector-recommendations-films
```

### Si tu as déjà un dossier local et que tu veux le lier au dépôt GitHub

Depuis le dossier du projet local :

```bash
git init
git remote add origin https://github.com/GemimaOndele/Projet_pgvector-recommendations-films.git
git add .
git commit -m "Initial commit: ajout du projet local"
git push -u origin main
```

> Adapter la branche (`main` ou `master`) selon la configuration du dépôt GitHub.

---

## Stack technique

- **Base de données** : PostgreSQL (>= 14) avec extension **pgvector**.  
- **Langage** : Python (>= 3.9).  
- **Librairies principales** :
  - `psycopg2-binary`
  - `numpy`
  - `pandas`
  - `scikit-learn`
  - `sentence-transformers`
  - `fastapi`
  - `uvicorn`

Un fichier `requirements.txt` sera fourni pour installer facilement les dépendances.

---

## Étapes globales du projet

- **1. Installation et configuration**
  - Installer PostgreSQL + pgvector (Windows : ajout des fichiers `pgvector` dans `lib` et `share/extension`, puis `CREATE EXTENSION vector;`).
  - Créer la base `filmsrec`.

- **2. Schéma de données**
  - Table `films` (id, title, year, genres, cast, synopsis, meta).  
  - Table `film_embeddings` (film_id, embedding vector(768)).

- **3. Ingestion des données (Rôle 1)**
  - Récupérer le dataset Hugging Face.  
  - Nettoyer, transformer au bon format.  
  - Insérer les films dans PostgreSQL via un script Python.

- **4. Embeddings & indexation (Rôle 2)**
  - Générer les embeddings pour chaque film.  
  - Créer l’index HNSW sur la colonne vectorielle.

- **5. API de recommandation (Rôle 3)**
  - Endpoints pour :  
    - recommander des films similaires à partir d’un `film_id`,  
    - recherche sémantique à partir d’une requête texte.

- **6. Évaluation & rapport (Rôle 4)**
  - Construire un protocole d’évaluation.  
  - Mesurer la qualité des recommandations.  
  - Rédiger le rapport final.

---

## À faire (TODO)

- Ajouter le script de téléchargement du dataset Hugging Face (`download_dataset.py`) et documenter le nom exact du dataset.
- Ajouter le script d’ingestion PostgreSQL (`ingest_films.py`).
- Créer `requirements.txt` et, éventuellement, un exemple de fichier `.env` (avec les variables, sans les secrets).
- Mettre en place les scripts d’embeddings, l’API FastAPI et le notebook d’évaluation.

