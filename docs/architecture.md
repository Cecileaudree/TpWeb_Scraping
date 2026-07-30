# Architecture du scraper

Ce projet est organisé autour d'une architecture en couches simples :

- `src/config.py` : lecture de la configuration depuis un fichier JSON
- `src/acquisition.py` : récupération de la page HTML, locale ou distante
- `src/extraction.py` : extraction des objets métiers depuis le DOM
- `src/normalization.py` : nettoyage, normalisation et déduplication
- `src/exporter.py` : export JSON
- `src/main.py` : enchaînement de la collecte
- `tests/` : vérifications sans réseau sur un échantillon stocké

## Flux de données

1. Charger la configuration
2. Récupérer la page de démarrage
3. Extraire les blocs produits
4. Normaliser les champs (prix, date, URL)
5. Dédupliquer par URL source
6. Exporter le résultat
7. Journaliser les totaux vus / exportés / rejetés
