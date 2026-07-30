# Scraper explicable

Ce projet propose un collecteur Web minimal en Python, structuré pour répondre aux attentes du TP : acquisition, extraction, normalisation, contrôle et export.

## Objectif

Ce scraper est conçu comme un exemple reproductible. Il collecte des fiches produits depuis une page HTML enregistrée dans `samples/sample_page.html`, puis exporte un fichier JSON normalisé.

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

Exécution limitée avec la page d'exemple :

```bash
python -m src.main --config config.example.json
```

L'export écrit par défaut dans `samples/sample_output.json`.

## Vérification sans réseau

Lancez les tests :

```bash
pytest
```

## Format de sortie

Le scraper produit un JSON contenant des objets avec :

- `id` : identifiant stable (URL source)
- `source_url` : URL de la page produit
- `title`
- `price`
- `currency`
- `availability`
- `collected_at`
- `published_date`

## Limites connues

- Exemple basé sur un HTML statique local
- Le parsing repose sur des selectors CSS simples
- Les champs absents sont rejetés pour éviter des enregistrements silencieusement incomplets

## Usage responsable

- Collecte localisée sur un fichier d'exemple
- Pause configurable entre requêtes
- Aucune authentification ou manipulation de données sensibles
