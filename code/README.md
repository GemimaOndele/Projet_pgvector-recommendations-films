# Dossier code/

Ce dossier contient les scripts Python du projet.

## Scripts disponibles

### 1. `download_dataset.py`

Télécharge le dataset de films depuis Hugging Face et le convertit en CSV.

**Utilisation :**

```bash
export HF_TOKEN="votre_token_huggingface"  # Optionnel si dataset public
python code/download_dataset.py
```

**Résultat :** Génère `data/films.csv`

---

### 2. `ingest_films.py`

Ingère les films depuis le CSV vers PostgreSQL.

**Prérequis :**
- Base PostgreSQL `filmsrec` créée
- Tables créées via `sql/schema.sql`
- Fichier `data/films.csv` présent

**Utilisation :**

```bash
# Définir les variables d'environnement PostgreSQL
export DB_USER="postgres"
export DB_PASSWORD="votre_mot_de_passe"
export DB_HOST="localhost"      # Optionnel (défaut: localhost)
export DB_PORT="5432"            # Optionnel (défaut: 5432)
export DB_NAME="filmsrec"        # Optionnel (défaut: filmsrec)

# Lancer l'ingestion
python code/ingest_films.py

# Ou avec un CSV personnalisé
python code/ingest_films.py --csv chemin/vers/films.csv
```

**Fonctionnalités :**
- Nettoyage automatique des genres (supporte plusieurs formats)
- Gestion des doublons (title + year)
- Insertion en batch pour de meilleures performances
- Messages de progression et statistiques

---

## Structure attendue du CSV

Le fichier `data/films.csv` doit contenir au minimum ces colonnes :

- `title` : Titre du film (requis)
- `year` : Année de sortie (optionnel)
- `genres` : Liste de genres (format: liste Python ou séparé par `|` ou `,`)
- `cast` : Liste d'acteurs (format: liste Python ou séparé par `|` ou `,`)
- `synopsis` : Synopsis du film (optionnel)

## Variables d'environnement

Pour éviter de hardcoder les identifiants, utilisez des variables d'environnement ou un fichier `.env` (non versionné).

Exemple de fichier `.env` (à créer localement, ne pas commiter) :

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=filmsrec
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
HF_TOKEN=votre_token_huggingface
```

Puis charger avec `python-dotenv` :

```python
from dotenv import load_dotenv
load_dotenv()
```

