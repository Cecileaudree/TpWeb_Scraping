# Scraper explicable

Ce projet propose un collecteur Web minimal en Python, structuré pour répondre aux attentes du TP : acquisition, extraction, normalisation, contrôle et export.

## Objectif

Ce scraper est aligné sur la cible S14 (Auckland War Memorial Museum). Il collecte une liste d'objets de collection, avec un mode local reproductible via `samples/sample_page.html`.

## Structure du projet

- `README.md`
- `src/` : code du collecteur
- `tests/` : vérifications unitaires sans réseau
- `samples/` : page de test et exemple de sortie
- `docs/` : architecture et usage IA
- `requirements.txt` : dépendances Python
- `config.example.json` : configuration sans secret

## Installation

1. Créez un environnement virtuel Python :

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

2. Installez les dépendances :

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Utilisation

Exécution avec la configuration fournie :

```bash
python -m src.main --config config.example.json
```

L'export écrit par défaut dans `samples/sample_output.json`.

## Contraintes S14 prises en compte

- Volume plafonné à 20 objets
- Scraping de liste uniquement (pas de parcours de pages détail)
- Champs minimaux de sortie : `title`, `category`, `date_text`, `url`
- Garde-fou Crawl-delay : pour `aucklandmuseum.com`, le délai configuré doit être au moins 30 secondes

## Vérification sans réseau

Lancez les tests :

```bash
pytest
```

## Format de sortie

Le scraper produit un JSON contenant des objets avec :

- `id` : identifiant stable (URL normalisée)
- `title`
- `category`
- `date_text`
- `url`
- `collected_at` : date et heure de collecte, au format ISO 8601 avec fuseau (UTC)

## Valeurs absentes vs valeurs vides

- Un champ optionnel (`category`, `date_text`) **absent** du HTML source est remplacé par la valeur `"inconnu"` et compté dans les statistiques comme champ manquant.
- Un champ **présent mais vide** reste une chaîne vide `""` : ce n'est pas la même situation qu'une absence, et le programme ne les confond pas.
- Un champ obligatoire (`title`, `url`) absent ou vide entraîne le **rejet** de l'objet.

## Pagination

La cible S14 utilisée en exemple tient sur une seule page (volume ≤ 20). Le
scraper sait néanmoins suivre une pagination si `target.next_page_selector`
est renseigné dans la configuration (ex: `a[rel='next']`), dans la limite de
`scrape.max_pages`.

## Limites connues

- Les sélecteurs CSS peuvent évoluer sur la cible réelle
- Le mode d'exemple local reste la base des tests automatisés
- Les entrées sans titre ou URL sont rejetées

## Usage responsable

- Collecte localisée sur un fichier d'exemple
- Pause configurable entre requêtes
- Aucune authentification ou manipulation de données sensibles
