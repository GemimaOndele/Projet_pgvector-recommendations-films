-- ============================================
-- Schéma de base de données pour le projet
-- Recommandation de films avec pgvector
-- ============================================

-- Création de la base (à exécuter en tant que superuser)
-- CREATE DATABASE filmsrec;

-- Connexion à la base
-- \c filmsrec

-- Activation de l'extension pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- Table principale : films
-- ============================================

CREATE TABLE IF NOT EXISTS films (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  year INT,
  genres TEXT[],        -- ex: {Drama,Romance}
  cast TEXT[],          -- ex: {Actor A,Actor B}
  synopsis TEXT,
  meta JSONB,           -- ex: {"runtime": 120, "country": "FR"}
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contrainte d'unicité sur title + year pour éviter les doublons
CREATE UNIQUE INDEX IF NOT EXISTS films_title_year_unique 
ON films (title, year) 
WHERE year IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS films_title_unique 
ON films (title) 
WHERE year IS NULL;

-- ============================================
-- Table des embeddings vectoriels
-- ============================================

CREATE TABLE IF NOT EXISTS film_embeddings (
  film_id INT PRIMARY KEY REFERENCES films(id) ON DELETE CASCADE,
  embedding vector(768),  -- Dimension pour sentence-transformers/all-mpnet-base-v2
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Indices pour améliorer les performances
-- ============================================

-- Indices GIN pour les tableaux et JSONB
CREATE INDEX IF NOT EXISTS idx_films_genres ON films USING GIN (genres);
CREATE INDEX IF NOT EXISTS idx_films_cast ON films USING GIN (cast);
CREATE INDEX IF NOT EXISTS idx_films_meta ON films USING GIN (meta);

-- Index sur l'année pour les filtres temporels
CREATE INDEX IF NOT EXISTS idx_films_year ON films (year);

-- Index sur le titre pour les recherches textuelles
CREATE INDEX IF NOT EXISTS idx_films_title ON films USING gin (to_tsvector('french', title));

-- ============================================
-- Index HNSW pour les recherches de similarité vectorielle
-- ============================================
-- ⚠️ IMPORTANT : Créer cet index APRÈS avoir inséré les embeddings
-- pour accélérer la création de l'index.

-- CREATE INDEX film_embeddings_hnsw_cosine
-- ON film_embeddings USING hnsw (embedding vector_cosine_ops);

-- ============================================
-- Fonction pour mettre à jour updated_at automatiquement
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_films_updated_at
    BEFORE UPDATE ON films
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Vues utiles pour les requêtes
-- ============================================

-- Vue pour les films avec leurs embeddings (si présents)
CREATE OR REPLACE VIEW films_with_embeddings AS
SELECT 
    f.id,
    f.title,
    f.year,
    f.genres,
    f.cast,
    f.synopsis,
    f.meta,
    CASE WHEN fe.film_id IS NOT NULL THEN true ELSE false END AS has_embedding
FROM films f
LEFT JOIN film_embeddings fe ON f.id = fe.film_id;

-- ============================================
-- Exemples de requêtes utiles
-- ============================================

-- Compter les films par année
-- SELECT year, COUNT(*) as count 
-- FROM films 
-- WHERE year IS NOT NULL 
-- GROUP BY year 
-- ORDER BY year DESC;

-- Films avec le plus de genres
-- SELECT title, year, array_length(genres, 1) as nb_genres, genres
-- FROM films
-- WHERE genres IS NOT NULL
-- ORDER BY nb_genres DESC
-- LIMIT 10;

-- Films sans synopsis
-- SELECT id, title, year 
-- FROM films 
-- WHERE synopsis IS NULL OR synopsis = '';

