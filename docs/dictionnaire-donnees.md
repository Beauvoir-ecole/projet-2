# Dictionnaire de données

> Ce document liste **toutes** les données manipulées par le projet, leur format et leur source. Il sert de référence unique avant et pendant le développement.

## Données stockées dans PostgreSQL

### Table `categories`

| Champ | Type | Contraintes | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Identifiant interne |
| `name` | VARCHAR(80) | NOT NULL, UNIQUE | Nom affiché (ex : « Catégorie A ») |
| `slug` | VARCHAR(80) | NOT NULL, UNIQUE | Identifiant URL en minuscules (ex : `categorie-a`) |

### Table `services`

| Champ | Type | Contraintes | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Identifiant interne |
| `title` | VARCHAR(120) | NOT NULL | Titre affiché du service |
| `description` | TEXT | NOT NULL | Description longue du service |
| `is_published` | BOOLEAN | NOT NULL, DEFAULT TRUE | Service visible côté public si vrai |
| `category_id` | INTEGER | NOT NULL, FOREIGN KEY → `categories.id`, ON DELETE CASCADE | Catégorie de rattachement |

## Données stockées dans MongoDB

### Collection `testimonials`

| Champ | Type | Contraintes | Description |
|---|---|---|---|
| `_id` | ObjectId | Auto-généré | Identifiant Mongo |
| `author` | String | requis, max 80 caractères | Nom de l'auteur du témoignage |
| `comment` | String | requis, max 1000 caractères | Texte du témoignage |
| `rating` | Integer | requis, entre 1 et 5 | Note sur 5 |
| `is_approved` | Boolean | défaut `false` | Affiché publiquement si `true` |
| `created_at` | DateTime UTC | défaut `now()` | Date de soumission |

## Données calculées / dérivées

| Donnée | Source | Description |
|---|---|---|
| Étoiles de la note | `testimonials.rating` | Affichage `★★★★☆` dans le template |
| URL d'image | `static/images/` + helper `find_image()` | Détection automatique de l'extension (`.svg`, `.jpg`, `.webp`, `.png`) |
| `current_year` | `datetime.now().year` (Python) | Année du footer |

## Données issues du formulaire de contact

Le formulaire de contact est externalisé via [Tally](https://tally.so) : les soumissions sont stockées **côté Tally**, pas dans nos bases. Tally est conforme RGPD (serveurs EU).
