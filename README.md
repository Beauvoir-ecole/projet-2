# Projet 2 — Site vitrine complet (front + back)

> Template pédagogique à destination des élèves de l'**École Beauvoir**.
> Ce projet est **uniquement un exercice**. Il n'est destiné ni à la production réelle ni à un usage commercial.

---

## À quoi sert ce template ?

C'est le **Projet 2** : la version étendue du Projet 1. On part de la même base (site vitrine HTML/CSS/JS responsive) et on ajoute une couche **back-end** : base relationnelle (PostgreSQL), base NoSQL (MongoDB), interface d'administration, modélisation MERISE.

L'idée est la même que le Projet 1 : tu changes peu de choses (couleurs, polices, images, textes, données de seed) et tu obtiens un site complet avec un mini back-office.

## Ce qu'il contient en plus du Projet 1

- **PostgreSQL via Neon** : 2 tables relationnelles (`categories` 1-N `services`) gérées via **SQLAlchemy**
- **MongoDB via Atlas** : 1 collection `testimonials` (témoignages clients avec modération)
- **Interface d'administration** sécurisée par login (`/admin`) : CRUD sur les services et catégories, modération des témoignages (approuver / dépublier / supprimer)
- **Architecture MVC** : Model (`models/`), View (`templates/`), Controller (routes Flask)
- **POO côté serveur** : classes `Service`, `Category`, `Testimonial` + leurs `Repository` respectifs
- **Documentation MERISE complète** : MCD, MLD (schéma + textuel), MPD, dictionnaire de données
- **Tests unitaires** (pytest) sur les repositories et les routes
- **Mode dégradé** : si Postgres ou Mongo ne sont pas configurés, le site affiche une page « oups, à configurer » au lieu de planter

## Stack technique

| Brique | Rôle |
|---|---|
| **Python 3 + Flask** | Serveur de développement et de production |
| **Flask-SQLAlchemy + pg8000** | ORM pour PostgreSQL (driver 100 % Python, aucune compilation) |
| **PyMongo** | Client MongoDB |
| **Jinja2** | Moteur de templates (inclus dans Flask) |
| **HTML5 + CSS3** | Structure et style des pages |
| **JavaScript (ES6+)** | Galerie filtrable, customizer en POO |
| **Git + GitHub** | Versionnage et dépôt distant |
| **Neon** | Hébergement PostgreSQL serverless gratuit |
| **MongoDB Atlas** | Hébergement MongoDB gratuit |
| **Render** | Hébergement de l'application Flask |
| **Tally** | Formulaire de contact externalisé |
| **pytest** | Tests unitaires |
| **python-dotenv** | Lecture des variables d'environnement depuis `.env` |

## Structure du projet

```
projet-2/
├── app.py                      # Serveur Flask + routes (Controllers)
├── requirements.txt
├── render.yaml                 # Config Render avec env vars
├── .env.example                # Modèle de variables d'environnement
├── .gitignore                  # .env est ignoré, .env.example est commité
├── README.md
├── deploiement.md              # Guide pas-à-pas
│
├── models/                     # COUCHE MODEL (POO)
│   ├── __init__.py
│   ├── db.py                   # Connexions Postgres + Mongo
│   ├── category.py             # Category + CategoryRepository (Postgres)
│   ├── service.py              # Service + ServiceRepository (Postgres)
│   └── testimonial.py          # Testimonial + TestimonialRepository (Mongo)
│
├── templates/                  # COUCHE VIEW (Jinja2)
│   ├── base.html               # squelette partagé
│   ├── index.html
│   ├── a-propos.html
│   ├── services.html           # liste les services depuis Postgres
│   ├── galerie.html
│   ├── temoignages.html        # liste les témoignages depuis Mongo + form
│   ├── contact.html
│   ├── mentions-legales.html
│   ├── 404.html
│   ├── db_missing.html         # page friendly si BD pas configurée
│   └── admin/                  # back-office
│       ├── login.html
│       ├── dashboard.html
│       ├── services.html
│       ├── service_form.html
│       └── testimonials.html
│
├── static/                     # FICHIERS STATIQUES
│   ├── css/
│   │   ├── variables.css       # ⭐ point unique de personnalisation
│   │   ├── style.css
│   │   └── customizations.css  # rempli par le QCM Personnalise-moi
│   ├── js/
│   │   ├── gallery.js          # POO côté client
│   │   └── customizer.js       # POO côté client
│   ├── images/                 # logo + image_1/2/3 + galerie
│   ├── robots.txt
│   └── sitemap.xml
│
├── seed/                       # JEUX DE DONNÉES DE TEST
│   ├── seed_postgres.py        # crée tables + données fictives
│   └── seed_mongo.py           # crée témoignages fictifs
│
├── tests/                      # TESTS unitaires (pytest)
│   ├── conftest.py
│   ├── test_models.py
│   └── test_routes.py
│
└── docs/                       # DOCUMENTATION MERISE
    ├── dictionnaire-donnees.md
    └── merise.md               # MCD + MLD (schéma & textuel) + MPD
```

## Démarrage express

Détails complets dans **[deploiement.md](deploiement.md)**.

```bash
# 1. Installer
python3 -m venv venv
source venv/bin/activate            # macOS / Linux / Git Bash
pip install -r requirements.txt

# 2. Configurer (optionnel pour démarrer)
cp .env.example .env
# Édite .env : FLASK_SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD
# (DATABASE_URL et MONGO_URL viendront plus tard)

# 3. Lancer
python app.py
# Ouvre http://localhost:5000
# Sans BD : les pages publiques marchent, /temoignages affiche le mode dégradé.
```

Pour activer la BD :
```bash
# Postgres (après avoir configuré DATABASE_URL)
python seed/seed_postgres.py

# Mongo (après avoir configuré MONGO_URL)
python seed/seed_mongo.py
```

## Tests

```bash
python -m pytest -q
```

Couvre la validation des entrées (POO Service/Testimonial), la création d'entités via les repositories, et le statut HTTP des routes publiques.

## Documentation MERISE

- [Dictionnaire de données](docs/dictionnaire-donnees.md) : champs, types, contraintes
- [MCD / MLD / MPD](docs/merise.md) : schémas en Mermaid + format textuel

## Personnaliser

Mêmes étapes que pour le Projet 1 (variables.css, images, lorem ipsum…) plus :

| Fichier | Ce que tu changes |
|---|---|
| `seed/seed_postgres.py` | Adapte les listes `CATEGORIES` et `SERVICES` à ton sujet |
| `seed/seed_mongo.py` | Adapte la liste `TESTIMONIALS` à ton sujet |
| `app.py` (classe `Site`) | Nom, slogan, description du site |
| `templates/temoignages.html` | Texte d'introduction |
| `templates/galerie.html` | Renomme « Catégorie A/B/C » |

Astuce IA : copie-colle un fichier de seed à Claude / ChatGPT avec :
> « Adapte ce fichier de seed Python pour un site de [ton sujet, ex : restaurant italien]. Garde exactement la même structure. »

## Accessibilité, éco-conception, RGPD

Identiques au Projet 1 : structure sémantique, alt sur toutes les images, focus visible, navigation clavier, mentions légales complètes avec données fictives, aucun tracker.

À toi de vérifier après personnalisation que les contrastes restent AA et que tes images font moins de 200 Ko.

## Que faire si tu es bloqué·e ?

1. Relis le message d'erreur — il pointe presque toujours la ligne exacte.
2. Pour les erreurs Flask : regarde le log dans le terminal qui fait tourner `python app.py`.
3. Pour les erreurs SQL : `python seed/seed_postgres.py` recrée tout proprement.
4. Demande à tes formateurs.

---

*Bon code !*
