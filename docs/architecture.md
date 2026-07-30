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
2. Récupérer la page de démarrage (et suivre la pagination si `next_page_selector` est configuré, jusqu'à `max_pages`)
3. Extraire les blocs d'objets de chaque page
4. Normaliser les champs S14 (`title`, `category`, `date_text`, `url`, `collected_at`)
5. Dédupliquer par URL source (id)
6. Limiter au volume configuré (`max_items`)
7. Exporter le résultat
8. Journaliser les totaux : pages parcourues, items vus, exportés, rejetés, doublons, champs manquants

## Règles S14 appliquées

- Plafond de volume : 20 objets maximum
- Collecte sur la liste uniquement
- Garde-fou Crawl-delay : 30 secondes minimum pour la cible Auckland Museum

## Décisions structurantes

- **Client HTTP direct (requests + BeautifulSoup) plutôt qu'un navigateur automatisé** : la cible S14 sert du HTML côté serveur (confirmé par le diagnostic), un navigateur complet (Playwright) aurait ajouté de la complexité sans bénéfice pour un contenu déjà présent dans le HTML initial.
- **Sélecteurs CSS plutôt que XPath** : plus lisibles et suffisants pour des classes/attributs stables ; alternative écartée : ancrage par position DOM (trop fragile).
- **Mode échantillon local (`sample_mode`) plutôt que collecte live systématique** : la cible réelle utilise une recherche par postback ASP.NET et interdit par `robots.txt` l'accès automatisé aux services qui chargent les résultats (`WebService.asmx`, `RESTService.svc`) ; le mode local garantit une vérification reproductible sans réseau.

## Exemple d'erreur gérée

Si une page (de démarrage ou de pagination) est inaccessible, `run()` journalise
l'erreur avec `logging.error` et arrête proprement le parcours au lieu de
faire planter le programme : les objets déjà collectés sont normalisés et
exportés normalement.
