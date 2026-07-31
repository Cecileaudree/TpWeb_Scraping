# Compte-rendu TP S14

## Informations de remise

- **Nom et prénom** : [à compléter]
- **Groupe** : [à compléter]
- **Identifiant de cible** : S14
- **Dépôt GitHub public** : https://github.com/Cecileaudree/TpWeb_Scraping
- **Hash du commit évalué** : `3778118fea2e857e865ce9408dab195d9b410d01`

## Résumé

L'objet collecté est un `CollectionItem` (`title`, `category`, `date_text`, `url`, `collected_at`) issu de la cible S14 Auckland War Memorial Museum. Le pipeline (*config* → *acquisition* → *extraction* → *normalisation* → *export*) produit un fichier JSON valide. La difficulté majeure sur la cible réelle résidait dans l'architecture dynamique de la recherche du musée, protégée par un pare-feu applicatif/WAF (erreurs HTTP 403 et blocage CORS lors d'accès direct ou API). La solution finale s'appuie sur une acquisition hybride via **Playwright**, capable de charger le HTML dynamique ou d'opérer en mode échantillon local déterministe pour garantir une répétabilité parfaite et respecter strictement les consignes d'éthique et de délai.

## 1. Cible et périmètre

- **Cible** : Auckland War Memorial Museum
- **URL de base** : `https://www.aucklandmuseum.com`
- **URL de départ utilisée dans ce dépôt** : `samples/sample_page.html` (mode local reproductible et autonome)
- **Objet collecté** : `CollectionItem`
- **Périmètre** : Liste d'objets uniquement (pas de crawl récursif sur les pages de détail)
- **Volume visé** : 20 objets maximum (`max_items = 20`)

## 2. Diagnostic initial

- **Rendu dynamique & JavaScript** : La cible réelle s'appuie sur une application Single Page (React/Next.js) et des composants dynamiques. Un moteur de recherche sans navigateur (`requests` / HTTP direct) échoue en renvoyant une coquille HTML vide. L'intégration de **Playwright (Chromium)** a permis de rendre le DOM JavaScript.
- **Vérification robots.txt** : Confirmée le 30/07/2026. Un `Crawl-delay: 30` est spécifié pour les robots génériques. Les sous-dossiers `/WebService.asmx/`, `/RESTService.svc/` et `/rest/` sont explicitement interdits.
- **Protection applicative (WAF / Anti-bot)** : Les tentatives d'accès direct automatisé à l'API backend (`api.aucklandmuseum.com`) ou à la recherche renvoient un blocage WAF (HTTP 403 Forbidden ou challenge Cloudflare).
- **Décision technique** :
  - Intégration d'un module d'acquisition **Playwright** pour gérer le rendu JS.
  - Bascule sur un **mode échantillon local (`sample_mode = true`)** pour l'évaluation et la suite de tests afin de garantir l'absence de blocage réseau et de respecter scrupuleusement l'éthique de collecte.

## 3. Architecture retenue

- **Modules de l'application** :
  - `src/config.py` : Charge, parse et valide les options JSON du fichier de configuration.
  - `src/acquisition.py` : Module d'acquisition utilisant Playwright (gestion des timeouts, rendu Chromium headless, fallback fichiers locaux).
  - `src/extraction.py` : Extrait les structures brutes (`RawItem`) depuis le DOM parsé par BeautifulSoup (ou structure JSON interceptée).
  - `src/normalization.py` : Nettoie les textes, résout les URL relatives, rejette les items invalides et élimine les doublons.
  - `src/exporter.py` : Exporte le résultat au format JSON.
  - `src/main.py` : Orchestre le pipeline global et applique les garde-fous S14.
- **Format de sortie** : JSON (`samples/sample_output.json`).

## 4. Stratégie d'extraction

- **Sélecteur d'item** : `.collection-item`
- **Sélecteurs de champs** :
  - `title` : `.item-title`
  - `url` : `.item-link` (récupération de l'attribut `href` ou extraction de l'élément direct)
  - `category` : `.item-category`
  - `date_text` : `.item-date`
- **Gestion des champs manquants** : Filtrage strict à la normalisation. Tout item ne possédant pas de `title` ou de `url` valide est automatiquement comptabilisé comme rejeté.
- **Déduplication** : Génération d'un identifiant stable (`id`) dérivé de l'URL normalisée.

## 5. Conformité et éthique

- **Respect du Crawl-delay (30s)** : Contrôle explicite exécuté dans `src/main.py` (`enforce_target_policies`) imposant au moins 30 secondes d'intervalle entre les requêtes vers `aucklandmuseum.com`.
- **Limitation du volume** : Application stricte du plafond `max_items` (limité à 20) après la phase de normalisation.
- **Données exclues** : Collecte cantonnée aux métadonnées publiques de premier niveau, exclusion des pages de détail, données personnelles et requêtes non sollicitées.

## 6. Résultats

| Vus | Exportés | Rejetés | Doublons | Champs manquants |
| :---: | :---: | :---: | :---: | :---: |
| 68 | 10 | 0 | 2 | 0 |

### Exemple d'objet JSON généré (`samples/sample_output.json`) :

```json
{
  "id": "/discover/collections/item-a",
  "title": "Tiki carved pendant",
  "category": "Ethnology",
  "date_text": "circa 1880",
  "url": "/discover/collections/item-a",
  "collected_at": "2026-07-30T13:59:21.127476+00:00"
}