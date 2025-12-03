## Guide d’installation et de configuration du projet

Ce document décrit l’installation de **PostgreSQL + pgvector**, la configuration de l’environnement **Python**, ainsi que la mise en place de la base `filmsrec` pour le projet de recommandation de films.

---

## 1. Prérequis système

- **PostgreSQL** : version **14+** recommandée.
- **pgvector** : extension PostgreSQL pour stocker des embeddings (type `vector`).
- **Python** : **3.9+** avec les bibliothèques nécessaires pour générer des embeddings.
- **Environnement virtuel** Python : recommandé pour isoler les dépendances du projet.

---

## 2. Installation de PostgreSQL et pgvector (Linux Ubuntu/Debian)

### 2.1 Installer PostgreSQL

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### 2.2 Créer la base de projet et activer pgvector

Connexion en `psql` puis exécution :

```sql
-- À exécuter dans psql
CREATE DATABASE filmsrec;
\c filmsrec
CREATE EXTENSION IF NOT EXISTS vector;
```

Vous pouvez vérifier la présence de l’extension avec :

```sql
\dx   -- doit lister 'vector'
```

---

## 3. Installation de pgvector sous Windows

Sur Windows, pgvector n’est pas fourni par défaut avec PostgreSQL. Il faut utiliser les binaires fournis par le projet **pgvector-windows**.

### 3.1 Vérifier la version de PostgreSQL

Dans **PowerShell** ou **CMD** :

```powershell
psql --version
```

Exemple de résultat :

```text
psql (PostgreSQL) 17.0
```

Notez la version majeure (par ex. `15`, `16`, `17`).  

### 3.2 Télécharger pgvector pour Windows

Aller sur la page des releases :  
[pgvector-windows releases](https://github.com/df7cb/pgvector-windows/releases)

Télécharger le fichier correspondant à votre version de PostgreSQL, par exemple :

- PostgreSQL 17 → `pgvector-0.8.1-pg17-x64.zip`
- PostgreSQL 16 → `pgvector-0.8.1-pg16-x64.zip`
- PostgreSQL 15 → `pgvector-0.8.1-pg15-x64.zip`

### 3.3 Décompresser et copier les fichiers

Dézipper le fichier téléchargé. Vous obtenez des dossiers similaires à :

- `lib/`
- `share/extension/`

Ensuite :

- Copier le **contenu** de `lib/` vers :  
  `C:\Program Files\PostgreSQL\<version>\lib\`
- Copier le **contenu** de `share/extension/` vers :  
  `C:\Program Files\PostgreSQL\<version>\share\extension\`

(*Remplacez `<version>` par votre version, ex. `17`.*)

### 3.4 Redémarrer le service PostgreSQL

Dans PowerShell **en administrateur** :

```powershell
net stop postgresql-x64-<version>
net start postgresql-x64-<version>
```

Exemple pour PostgreSQL 17 :

```powershell
net stop postgresql-x64-17
net start postgresql-x64-17
```

### 3.5 Activer l’extension dans la base

Dans `pgAdmin` ou `psql` :

```sql
CREATE DATABASE filmsrec;
\c filmsrec
CREATE EXTENSION IF NOT EXISTS vector;
```

Si tout est correct, la commande renvoie :

```text
CREATE EXTENSION
```

---

## 4. Environnement Python

### 4.1 Création d’un environnement virtuel

Dans le répertoire du projet :

```bash
python3 -m venv venv
source venv/bin/activate      # Linux / macOS
# ou sous Windows PowerShell
# .\venv\Scripts\Activate.ps1
```

### 4.2 Installation des dépendances

Le fichier `requirements.txt` contient les librairies nécessaires, par exemple :

- `psycopg2-binary`
- `numpy`
- `pandas`
- `scikit-learn`
- `sentence-transformers`
- `fastapi`
- `uvicorn`

Installez-les avec :

```bash
pip install -r requirements.txt
```

---

## 5. Schéma de données PostgreSQL

Dans la base `filmsrec`, créer les tables principales :

```sql
CREATE TABLE films (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  year INT,
  genres TEXT[],        -- ex: {Drama,Romance}
  cast TEXT[],          -- ex: {Actor A,Actor B}
  synopsis TEXT,
  meta JSONB            -- ex: {"runtime": 120, "country": "FR"}
);

-- Dimension selon le modèle choisi (ex: 768)
CREATE TABLE film_embeddings (
  film_id INT PRIMARY KEY REFERENCES films(id) ON DELETE CASCADE,
  embedding vector(768)
);
```

Indices utiles pour accélérer certains filtres :

```sql
CREATE INDEX ON films USING GIN (genres);
CREATE INDEX ON films USING GIN (cast);
CREATE INDEX ON films USING GIN (meta);
```

---

## 6. Première mise en route du projet

1. **Cloner le dépôt** :

   ```bash
   git clone https://github.com/GemimaOndele/Projet_pgvector-recommendations-films.git
   cd Projet_pgvector-recommendations-films
   ```

2. **Créer et activer l’environnement virtuel**, puis installer les dépendances :

   ```bash
   python3 -m venv venv
   source venv/bin/activate          # ou .\venv\Scripts\Activate.ps1 sous Windows
   pip install -r requirements.txt
   ```

3. **Créer la base et activer l’extension `vector`** (si ce n’est pas déjà fait) :

   ```sql
   CREATE DATABASE filmsrec;
   \c filmsrec
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

4. **Créer les tables** `films` et `film_embeddings` (section 5 ci-dessus).

5. **Ingestion des données** :
   - Préparer un fichier `films.csv` (ou un dataset Hugging Face converti en CSV).
   - Utiliser un script d’ingestion Python (par ex. `scripts/ingestion.py`) pour insérer les films dans la table `films`.

6. **Embeddings et indexation** :
   - Lancer le script de génération des embeddings (par ex. `scripts/embeddings.py`).
   - Créer l’index HNSW :

     ```sql
     CREATE INDEX film_embeddings_hnsw_cosine
     ON film_embeddings USING hnsw (embedding vector_cosine_ops);
     ```

7. **API de démonstration** :
   - Démarrer l’API FastAPI (par ex.) :

     ```bash
     uvicorn app:app --reload
     ```

   - Tester les endpoints de recommandation et de recherche sémantique.

---

## 7. Bonnes pratiques et maintenance

- **Créer l’index HNSW après l’insertion massive** des embeddings pour réduire le temps de création.
- Exécuter régulièrement :

  ```sql
  VACUUM ANALYZE film_embeddings;
  ```

  pour aider l’optimiseur PostgreSQL.

- Combiner les requêtes de similarité avec des **filtres relationnels** (`WHERE year >= 2000`, `WHERE 'Drama' = ANY(genres)`, etc.) pour réduire le domaine de recherche.
- Gérer les **droits d’accès** : 
  - accès en lecture pour l’API,
  - accès en écriture réservé aux scripts d’ingestion / batch.


