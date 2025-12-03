# Dossier data/

Ce dossier contient les fichiers de données du projet.

## Fichiers

- `films.csv` : Dataset de films téléchargé depuis Hugging Face (Gkop/moviemood-dataset)

⚠️ **Note** : Le fichier `films.csv` n'est **pas versionné** dans Git car il est trop volumineux.  
Pour le générer, exécutez le script `code/download_dataset.py` :

```bash
export HF_TOKEN="votre_token_huggingface"
python code/download_dataset.py
```

Le fichier sera créé automatiquement dans ce dossier.

