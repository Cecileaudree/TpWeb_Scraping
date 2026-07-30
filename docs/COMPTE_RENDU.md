# Compte-rendu TP S14

**Dépôt GitHub public** : https://github.com/Cecileaudree/TpWeb_Scraping
**Hash du commit évalué** : `2e730d2dd646b46a38f0966024bd5427dfb2ad87`

## 1. Cible et périmètre

- Cible: Auckland War Memorial Museum (S14)
- URL de base: https://www.aucklandmuseum.com
- URL de départ utilisée dans ce dépôt: `samples/sample_page.html` (mode local reproductible)
- Objet collecté: CollectionItem
- Périmètre: liste uniquement, pas de collecte des pages détail
- Volume visé: 20 objets maximum

## 2. Diagnostic initial

- Vérification du rendu sans JavaScript: validée sur l'échantillon local (`sample_mode = true`), qui est statique et parsable sans navigateur.
- Vérification robots.txt (refaite le 30/07/2026, en direct) : `Crawl-delay: 30` confirmé pour tout robot générique ; endpoints `WebService.asmx/`, `RESTService.svc/`, `rest/` explicitement interdits (`disallow`).
- Preuve : la page `https://www.aucklandmuseum.com/discover/collections` récupérée manuellement (navigateur) montre une page hub (bannière, carrousel, liens) — ce n'est pas une liste de `CollectionItem`. La recherche réelle fonctionne par **postback ASP.NET** (`__doPostBack`, `__VIEWSTATE`), les résultats ne sont donc pas dans une URL directement scrapable.
- Une tentative d'accès automatisé (GET simple) à cette page et à `/discover/collections/search` a été bloquée par une protection anti-bot (403 Forbidden), constatée indépendamment du robots.txt.
- Crawl-delay observé / imposé: 30 secondes minimum.
- Décision technique (HTTP direct / navigateur): HTTP direct + parsing BeautifulSoup pour l'échantillon local ; pas d'automatisation navigateur dans cette version, car le blocage constaté est un pare-feu applicatif, pas un rendu JavaScript à contourner.

## 3. Architecture retenue

- Modules utilisés: `src/config.py`, `src/acquisition.py`, `src/extraction.py`, `src/normalization.py`, `src/exporter.py`, `src/main.py`.
- Rôle de chaque module:
	- `config`: charge et valide la configuration JSON.
	- `acquisition`: récupère la page (locale ou distante) avec délai configurable.
	- `extraction`: extrait les champs bruts via sélecteurs CSS.
	- `normalization`: nettoie, normalise les URL, filtre les items invalides et déduplique.
	- `exporter`: écrit la sortie JSON.
	- `main`: orchestre le pipeline et applique les garde-fous S14.
- Format de sortie: JSON (`samples/sample_output.json`).

## 4. Stratégie d'extraction

- Sélecteur item: `.collection-item`
- Sélecteurs de champs:
	- `title`: `.item-title`
	- `url`: `.item-link` (extraction depuis `href`)
	- `category`: `.item-category`
	- `date_text`: `.item-date`
- Gestion des champs manquants: les entrées sans `title` ou sans `url` sont rejetées à la normalisation.
- Déduplication: par identifiant stable (`id`) dérivé de l'URL normalisée.

## 5. Conformité et éthique

- Respect Crawl-delay 30s: garde-fou explicite dans `src/main.py` (`enforce_target_policies`) qui lève une erreur si `delay_seconds < 30` pour `aucklandmuseum.com`.
- Limitation du volume: application de `max_items` après normalisation (`normalized = normalized[:max_items]`), avec valeur configurée à 20.
- Données volontairement exclues: contenu des pages détail, authentification, données non demandées par S14.

## 6. Résultats

| Vus | Exportés | Rejetés | Doublons | Champs manquants |
|---|---|---|---|---|
| 3 | 3 | 0 | 0 | 0 |

- Exemple d'objet JSON:

```json
{
	"id": "/discover/collections/item-a",
	"title": "Tiki carved pendant",
	"category": "Ethnology",
	"date_text": "circa 1880",
	"url": "/discover/collections/item-a",
	"collected_at": "2026-07-30T13:59:21.127476+00:00"
}
```

## 7. Difficultés et arbitrages

- Difficultés rencontrées:
	- aligner un code initialement orienté "produits" vers le schéma S14 `CollectionItem`;
	- stabiliser la suite de tests en évitant la collecte de scripts réseau.
- Arbitrages techniques:
	- privilégier un mode local déterministe (`sample_mode`) pour valider le pipeline;
	- conserver un scraper simple et explicable (HTTP + BeautifulSoup) plutôt qu'un navigateur automatisé.
- Limites connues:
	- les sélecteurs CSS peuvent évoluer sur la cible réelle;
	- ce dépôt ne contient pas encore une campagne d'exécution complète sur la cible distante en production.

## 8. Tests et validation

- Tests exécutés: `pytest` sur `tests/test_scraper.py` (découverte limitée à `tests/` via `pytest.ini`).
- Résultats: 6 tests exécutés, 6 réussis.
- Points vérifiés:
	- extraction du nombre d'items;
	- conformité du schéma S14 normalisé (y compris `collected_at`);
	- distinction champ absent ("inconnu") vs champ présent mais vide ("");
	- rejet des entrées invalides et déduplication (avec compteurs vus/rejetés/doublons);
	- comportement de limitation du volume;
	- absence de pagination quand aucun sélecteur n'est configuré.
- Exemple d'erreur gérée : une page inaccessible (page de démarrage ou de pagination) est journalisée (`logging.error`) et interrompt proprement le parcours sans faire planter le programme ; les objets déjà collectés sont tout de même exportés.

## 9. Usage IA

- Outils IA utilisés: GitHub Copilot / ChatGPT.
- Ce qui a été généré:
	- propositions de structuration modulaire;
	- assistance sur l'adaptation du schéma de données;
	- assistance pour la rédaction technique (README, architecture, compte-rendu).
- Ce qui a été vérifié/manuellement validé:
	- conformité avec les contraintes S14;
	- cohérence des sélecteurs avec l'échantillon HTML;
	- exécution des tests et validation des résultats.
