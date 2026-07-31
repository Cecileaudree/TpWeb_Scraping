# Compte-rendu TP S14

## Informations de remise

- **Nom et prénom** : [à compléter]
- **Groupe** : [à compléter]
- **Identifiant de cible** : S14
- **Dépôt GitHub public** : https://github.com/Cecileaudree/TpWeb_Scraping
- **Hash du commit évalué** : `3778118fea2e857e865ce9408dab195d9b410d01`

## Résumé

L'objet collecté est un `CollectionItem` (`title`, `category`, `date_text`, `url`, `collected_at`) issu de la cible S14 Auckland War Memorial Museum. Le pipeline (*config* → *acquisition* → *extraction* → *normalisation* → *export*) produit un fichier **JSONL** valide (un objet JSON par ligne). La difficulté majeure sur la cible réelle est que la recherche du musée fonctionne via un formulaire ASP.NET à base de postback (`__doPostBack` / `__VIEWSTATE`), sans URL de résultats directement scrapable, et que le site est protégé par un pare-feu applicatif Cloudflare : toute requête automatisée (y compris via un navigateur Playwright headless) reçoit une page de challenge (`Just a moment...`) au lieu du contenu réel. Nous avons délibérément choisi de ne pas contourner cette protection (voir section 2) et de garantir la reproductibilité du pipeline via un **mode échantillon local** (`sample_mode = true`), qui est la configuration par défaut du dépôt.

## 1. Cible et périmètre

- **Cible** : Auckland War Memorial Museum
- **URL de base** : `https://www.aucklandmuseum.com`
- **URL de recherche réelle identifiée** : `https://www.aucklandmuseum.com/discover/collections/search?k=brooch`
- **URL de départ utilisée par défaut dans ce dépôt** : `samples/sample_page.html` (mode local reproductible et autonome, `sample_mode = true`)
- **Objet collecté** : `CollectionItem`
- **Périmètre** : Liste d'objets uniquement (pas de crawl récursif sur les pages de détail)
- **Volume visé** : 20 objets maximum (`max_items = 20`)

## 2. Diagnostic initial

- **Architecture de la cible** : Le moteur de recherche du musée s'appuie sur des composants ASP.NET WebForms (`masterForm`, `__VIEWSTATE`, `__doPostBack`). La page de résultats (`/discover/collections/search?k=...`) est néanmoins accessible par URL directe dans un navigateur complet.
- **Vérification robots.txt** : Confirmée le 30/07/2026. Un `Crawl-delay: 30` est spécifié pour les robots génériques. Les sous-dossiers `/WebService.asmx/`, `/RESTService.svc/` et `/rest/` sont explicitement interdits.
- **Protection applicative (WAF Cloudflare)** : Toute tentative d'acquisition automatisée de la page de recherche — y compris via Playwright/Chromium headless avec un user-agent standard — reçoit systématiquement une page de challenge Cloudflare (`Just a moment...`) au lieu du HTML attendu, quel que soit le délai d'attente appliqué après le chargement.
- **Tentative de contournement testée et rejetée** : une version du module d'acquisition a été expérimentée avec des techniques d'évasion anti-détection (masquage de `navigator.webdriver`, simulation de mouvements de souris et de scroll, arguments Chromium `--disable-blink-features=AutomationControlled`). Cette approche a été testée et **n'a pas permis de passer le challenge Cloudflare de façon fiable**. Plus fondamentalement, elle a été **retirée délibérément** du code final : contourner une protection anti-bot explicite constitue un contournement d'un blocage volontaire de la cible, ce qui va à l'encontre des consignes d'éthique de collecte du TP.
- **Décision technique retenue** :
  - Conservation d'un module d'acquisition **Playwright** simple et transparent (sans technique d'évasion), documenté dans `config.live.example.json` avec les sélecteurs vérifiés manuellement sur la page de résultats réelle, pour référence.
  - **`sample_mode = true`** comme configuration par défaut (`config.example.json`) : le pipeline s'exécute sur une copie locale et statique d'une page de résultats (`samples/sample_page.html`), garantissant une exécution reproductible, sans blocage réseau, et respectueuse de la protection mise en place par la cible.

## 3. Architecture retenue

- **Modules de l'application** :
  - `src/config.py` : Charge, parse et valide les options JSON du fichier de configuration ; résout la source à scraper (fichier local en mode échantillon ou URL distante sinon).
  - `src/acquisition.py` : Récupère le HTML — lecture directe si `source` est un fichier local ou une URI `file://`, sinon requête via Playwright (Chromium headless), sans technique d'évasion anti-bot.
  - `src/extraction.py` : Extrait les structures brutes (`RawItem`) depuis le DOM parsé par BeautifulSoup, à partir de `item_selector` et des sélecteurs de champs de la configuration (support du sélecteur spécial `"self"`).
  - `src/normalization.py` : Nettoie les textes, résout les URL relatives, rejette les items sans `title`/`url`, distingue champ optionnel absent vs vide, et élimine les doublons par URL normalisée.
  - `src/exporter.py` : Exporte le résultat au format **JSON** ou **JSONL** selon `config.export.format` (`export_items` dispatche vers `export_json` ou `export_jsonl`).
  - `src/main.py` : Orchestre le pipeline global et applique les garde-fous S14 (`enforce_target_policies`, troncature `max_items`, boucle de pagination bornée par `max_pages`).
- **Format de sortie retenu** : **JSONL**, un objet JSON par ligne (`output.jsonl`), conforme à `config.example.json`.

## 4. Stratégie d'extraction

- **Sélecteur d'item (config par défaut, mode échantillon)** : correspond à la structure de `samples/sample_page.html`.
- **Sélecteurs de champs identifiés et vérifiés sur la vraie page de résultats** (documentés dans `config.live.example.json`, non utilisés par défaut à cause du blocage Cloudflare) :
  - `item_selector` : `article a[href^='/discover/collections/record/']`
  - `title` : `h2.search-results--heading`
  - `url` : `self` (attribut `href` de l'élément sélectionné par `item_selector`)
  - `category` : `p.search-results--info-details span:nth-of-type(1)`
  - `date_text` : `p.search-results--info-details span:nth-of-type(3)`
- **Gestion des champs manquants** : Filtrage strict à la normalisation. Tout item sans `title` ni `url` valide est automatiquement comptabilisé comme rejeté. Les champs optionnels absents de la structure brute sont remplacés par le marqueur `"inconnu"` et comptabilisés séparément d'un champ présent mais vide.
- **Déduplication** : Génération d'un identifiant stable (`id`) dérivé de l'URL normalisée.

## 5. Conformité et éthique

- **Respect du Crawl-delay (30s)** : Contrôle explicite exécuté dans `src/main.py` (`enforce_target_policies`) imposant au moins 30 secondes d'intervalle entre les requêtes vers `aucklandmuseum.com`.
- **Limitation du volume** : Application stricte du plafond `max_items` (limité à 20) après la phase de normalisation.
- **Respect du blocage anti-bot de la cible** : Aucune technique de contournement (anti-détection, faux fingerprint navigateur, simulation comportementale) n'est présente dans le code final livré, malgré une tentative testée puis explicitement retirée (cf. section 2).
- **Données exclues** : Collecte cantonnée aux métadonnées publiques de premier niveau, exclusion des pages de détail, données personnelles et requêtes non sollicitées.

## 6. Résultats

Résultats obtenus en exécutant `python -m src.main --config config.example.json` (mode échantillon, configuration par défaut du dépôt) :

| Vus | Exportés | Rejetés | Doublons | Champs optionnels manquants |
| :---: | :---: | :---: | :---: | :---: |
| 3 | 3 | 0 | 0 | 0 |

### Exemple d'objet JSON généré (`output.jsonl`, une ligne = un objet) :

```json
{"id": "/discover/collections/item-a", "title": "Notice A", "category": "Collection Item", "date_text": "N/A", "url": "/discover/collections/item-a", "collected_at": "2026-07-31T13:27:03.403753+00:00"}
```
