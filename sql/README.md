# Dossier sql/

Ce dossier contient les scripts SQL pour la création et la gestion du schéma de base de données.

## Fichiers

- **`schema.sql`** : Script complet pour créer les tables, indices, vues et fonctions nécessaires au projet.

## Utilisation

### 1. Créer la base de données

Dans `psql` ou `pgAdmin`, en tant que superuser :

```sql
CREATE DATABASE filmsrec;
```

### 2. Exécuter le schéma

```bash
psql -d filmsrec -f sql/schema.sql
```

Ou depuis `psql` :

```sql
\c filmsrec
\i sql/schema.sql
```

### 3. Vérifier l'installation

```sql
-- Vérifier que l'extension pgvector est active
\dx

-- Vérifier les tables créées
\dt

-- Vérifier les indices
\di
```

## Notes importantes

- L'index HNSW (`film_embeddings_hnsw_cosine`) est commenté dans le script initial.
- **Créer cet index APRÈS** avoir inséré tous les embeddings pour accélérer la création.
- Les contraintes d'unicité sur `title` + `year` évitent les doublons lors de l'ingestion.

