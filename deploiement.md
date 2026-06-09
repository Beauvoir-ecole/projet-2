# Guide pas-à-pas : installation, personnalisation et déploiement

> Ce guide te conduit de **« je viens juste de cloner le projet »** jusqu'à **« mon site est en ligne avec sa base PostgreSQL et sa base MongoDB »**.
> Suis-le **dans l'ordre, ligne par ligne**.

---

## Sommaire

1. [Préparer tes outils](#1-préparer-tes-outils)
2. [Créer tes comptes](#2-créer-tes-comptes)
3. [Récupérer le projet](#3-récupérer-le-projet)
4. [Installer les dépendances Python](#4-installer-les-dépendances-python)
5. [Configurer le fichier `.env`](#5-configurer-le-fichier-env)
6. [Mettre en place PostgreSQL (Neon)](#6-mettre-en-place-postgresql-neon)
7. [Mettre en place MongoDB Atlas](#7-mettre-en-place-mongodb-atlas)
8. [Lancer le projet en local](#8-lancer-le-projet-en-local)
9. [Personnaliser : étape par étape](#9-personnaliser--étape-par-étape)
10. [Vérifier localement](#10-vérifier-localement)
11. [Publier sur GitHub](#11-publier-sur-github)
12. [Déployer sur Render](#12-déployer-sur-render)
13. [Après déploiement](#13-après-déploiement)
14. [Workflow quotidien](#14-workflow-quotidien)

---

## 1. Préparer tes outils

À installer une seule fois. **Suis la sous-section qui correspond à ton OS.**

> ⚠️ **Sous Windows : utilise Git Bash pour toutes les commandes de ce guide.** Git Bash est installé automatiquement avec Git (voir §1.2). Toutes les commandes (`cd`, `source`, `python`…) y fonctionnent comme sur macOS/Linux, contrairement à CMD ou PowerShell.

### 1.1. Python 3 (obligatoire)

**macOS** :
```bash
python3 --version
```
Si la version est < 3.10 ou si Python n'est pas installé : `brew install python` ou télécharge depuis [python.org/downloads/macos](https://www.python.org/downloads/macos/).

**Windows** :
1. Télécharge depuis [python.org/downloads/windows](https://www.python.org/downloads/windows/).
2. ⚠️ **Coche absolument « Add Python to PATH »** dans la première fenêtre de l'installateur.
3. Vérifie dans Git Bash : `python --version`.

> 💡 Sous Windows, la commande est `python` (sans `3`). Dans les commandes de ce guide qui disent `python3`, remplace par `python`.

**Linux** : `sudo apt install python3 python3-venv python3-pip`.

### 1.2. Git + Git Bash (obligatoire)

**macOS** : `git --version` ; sinon `brew install git`.

**Windows** :
1. Télécharge **Git for Windows** depuis [git-scm.com/download/win](https://git-scm.com/download/win).
2. Lance l'installateur, garde les options par défaut.
3. **Git Bash s'installe automatiquement**. Ouvre-le depuis le menu Démarrer.

**Linux** : `sudo apt install git`.

**Configurer ton identité** (une fois pour toutes) :
```bash
git config --global user.name "Ton Prénom Nom"
git config --global user.email "ton.email@example.com"
```

### 1.3. VS Code

[code.visualstudio.com](https://code.visualstudio.com) — extensions à installer : **Python**, **Jinja**, **SQLite Viewer** (pour inspecter la base SQLite locale de dev).

> 💡 **Windows** : ouvre Git Bash directement depuis VS Code via *Terminal → New Terminal*, puis sélecteur en haut à droite → « Git Bash ».

---

## 2. Créer tes comptes

À faire une seule fois.

### 2.1. GitHub
Inscris-toi sur [github.com](https://github.com).

### 2.2. Render
[render.com](https://render.com) → **« Get Started »** → **« Sign up with GitHub »**.

### 2.3. Neon (PostgreSQL)
[neon.tech](https://neon.tech) → **« Sign up »** → connecte avec GitHub. Le plan gratuit suffit pour ce projet.

### 2.4. MongoDB Atlas
[mongodb.com/atlas/register](https://www.mongodb.com/atlas/register) → inscris-toi. Tu choisiras le cluster gratuit (M0) à l'étape §7.

### 2.5. Tally
[tally.so](https://tally.so) → inscris-toi (gratuit).

---

## 3. Récupérer le projet

### 3.1. Créer ton dépôt GitHub
1. GitHub → `+` en haut à droite → **« New repository »**.
2. Nom : `mon-projet-2` (par exemple).
3. **Coche Private** si tu veux rester discret.
4. **NE coche pas** « Add a README ».
5. **« Create repository »**.

### 3.2. Cloner le template

Dans ton terminal (macOS Terminal / Git Bash / Linux shell), clone le dépôt de ta formatrice :

```bash
cd ~/Documents
git clone https://github.com/Beauvoir-ecole/projet-2.git mon-projet-2
cd mon-projet-2
```

⚠️ Tu peux remplacer `mon-projet-2` par le nom de dossier que tu veux.

### 3.3. Relier le projet à TON dépôt

Le projet que tu viens de cloner est encore relié au dépôt de ta formatrice (tu ne peux pas y envoyer ton travail). On le relie au **tien** :

```bash
git remote set-url origin https://github.com/TON-PSEUDO/mon-projet-2.git
git branch -M main
git push -u origin main
```

⚠️ Remplace `TON-PSEUDO` et `mon-projet-2` par tes vraies valeurs.

À partir de là, **chaque fois que tu modifies ton site**, tu sauvegardes ton travail sur GitHub :

```bash
git add .
git commit -m "Décris ce que tu as changé"
git push
```

Si GitHub te demande un mot de passe : génère un **token** dans *Settings → Developer settings → Personal access tokens → Tokens (classic)*, coche `repo`, copie le token, et utilise-le comme mot de passe.

### 3.4. Activer le garde-fou anti-secret (recommandé)

Ce projet manipule des secrets (clé Flask, mots de passe, URL de bases de données). Un petit script **bloque un commit si un secret est détecté**. Active-le **une fois** (à refaire après chaque nouveau clone) :

```bash
git config core.hooksPath hooks
```

Si tu essaies ensuite de commiter un secret par erreur (ou un fichier `.env`), Git refuse et t'explique où il l'a vu.

---

## 4. Installer les dépendances Python

### 4.1. Créer le venv
```bash
python3 -m venv venv
```

### 4.2. Activer le venv

- **macOS / Linux / Git Bash (Windows)** :
  ```bash
  source venv/bin/activate
  ```
  Sous Git Bash Windows, le chemin est `source venv/Scripts/activate`.
- **Windows PowerShell** :
  ```powershell
  venv\Scripts\Activate.ps1
  ```

Tu sauras que c'est activé quand `(venv)` apparaît au début de la ligne.

### 4.3. Installer les paquets
```bash
pip install -r requirements.txt
```

Ça installe : Flask, Flask-SQLAlchemy, pg8000, pymongo, python-dotenv, gunicorn, pytest.

> 💡 Le driver PostgreSQL utilisé est **pg8000**, écrit 100 % en Python : il s'installe partout sans rien compiler (contrairement à `psycopg2`, qui pose souvent problème sur certaines machines et sur Render). Tu n'as rien de spécial à faire : colle simplement ton URL Neon dans `.env`, le projet s'occupe du reste.

---

## 5. Configurer le fichier `.env`

Le fichier `.env.example` est versionné comme **modèle**. Tu en fais une copie nommée `.env` qui restera **ignorée par Git** (ne sera jamais publiée).

```bash
cp .env.example .env
```

Ouvre `.env` dans VS Code et remplis :

```env
FLASK_SECRET_KEY=...               # Génère avec : python -c "import secrets; print(secrets.token_hex(32))"
ADMIN_USERNAME=admin
ADMIN_PASSWORD=mon-mdp-fort

DATABASE_URL=                       # Tu rempliras ça à l'étape 6
MONGO_URL=                          # Tu rempliras ça à l'étape 7
MONGO_DB_NAME=projet_2
```

⚠️ **Ne pousse jamais `.env` sur Git** — il est déjà dans `.gitignore`.

---

## 6. Mettre en place PostgreSQL (Neon)

### 6.1. Créer un projet Neon
1. Connecte-toi sur [console.neon.tech](https://console.neon.tech).
2. **« Create Project »**.
3. Nom : `mon-projet-2`. Région : la plus proche de toi (Frankfurt si tu es en Europe).
4. **« Create Project »**.

### 6.2. Récupérer la connection string
Sur la page du projet, en haut à droite : **« Connection string »** → copie la chaîne qui ressemble à :
```
postgresql://USER:PASSWORD@HOST.neon.tech/dbname?sslmode=require
```

Colle-la dans `.env` sous `DATABASE_URL`.

### 6.3. Créer les tables et insérer les données de test
Dans ton terminal (venv activé) :
```bash
python seed/seed_postgres.py
```

Tu dois voir : `✅ Inserted 3 categories and 4 services.`

> 💡 Sans `DATABASE_URL` dans `.env`, le seed bascule automatiquement sur SQLite (`dev.db` créé à la racine). Pratique pour tester en local sans toucher à Neon. **Mais pour un vrai déploiement avec une vraie base de données PostgreSQL, tu dois bien faire les §6.4 et §6.5 ci-dessous sur Neon.**

### 6.4. Créer un utilisateur applicatif avec droits limités
Par défaut, ta `DATABASE_URL` utilise le compte propriétaire qui peut tout faire (y compris supprimer les tables). Pour un projet sérieux, on crée un utilisateur dédié à l'application avec **uniquement** les droits de lecture et d'écriture sur les données.

1. Sur Neon → **« SQL Editor »** (menu de gauche).
2. Colle ce bloc et clique **« Run »** :
   ```sql
   CREATE USER app_user WITH PASSWORD 'change-moi-pour-un-mot-de-passe-fort';
   GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
   GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
   ```
3. C'est tout. Tu as maintenant un user `app_user` qui peut lire et modifier les données mais qui **ne peut pas** supprimer les tables ni créer de nouvelles tables.
4. (Optionnel) Pour utiliser ce user dans ton appli : remplace `USER` et `PASSWORD` dans ta `DATABASE_URL` par `app_user` et le mot de passe choisi.

> Note pour ton dossier projet : tu pourras expliquer au jury que tu as séparé le compte d'administration (qui crée les tables avec `seed_postgres.py`) du compte de production (qui ne fait que lire/écrire).

### 6.5. Sauvegarde et restauration
Neon fait des **sauvegardes automatiques en continu** : sur le plan gratuit, tu peux restaurer ta base à n'importe quel moment des **7 derniers jours**. Aucune commande à taper.

Pour le vérifier :
1. Sur Neon → **« Branches »** → ton projet.
2. Tu vois l'option **« Restore »** : c'est l'interface qui te permet de revenir en arrière en un clic.

> Note pour ton dossier projet : tu peux mentionner que ta base bénéficie d'un **PITR (Point-in-Time Recovery)** automatique sur 7 jours, et joindre une capture d'écran de l'écran « Branches → Restore » comme preuve.

---

## 7. Mettre en place MongoDB Atlas

### 7.1. Créer un cluster gratuit
1. Connecte-toi sur [cloud.mongodb.com](https://cloud.mongodb.com).
2. **« Build a Database »** → choisis **M0 (Free)**.
3. Provider : AWS. Région : la plus proche (Frankfurt).
4. **« Create Deployment »**.

### 7.2. Créer un utilisateur de base
On te propose un écran « Security Quickstart ».
1. **Username** : `projet-user` (ou ce que tu veux).
2. **Password** : génère-en un fort, **note-le quelque part**.
3. **« Create User »**.

### 7.3. ⚠️ Autoriser les connexions externes (étape critique !)
Sur la même page Security Quickstart, section **« Where would you like to connect from? »** :

- Choisis **« My Local Environment »** ET ajoute aussi l'entrée **`0.0.0.0/0`** (Allow access from anywhere).

> 💡 **Pourquoi `0.0.0.0/0` ?** Render utilise des IP dynamiques qui changent à chaque déploiement. Si tu ne mets pas `0.0.0.0/0`, ton app en ligne ne pourra pas se connecter à Atlas. C'est moins sécurisé mais acceptable pour un projet pédagogique. La sécurité est assurée par le mot de passe de l'utilisateur DB.

Pour ajouter `0.0.0.0/0` plus tard si tu l'as oublié : menu de gauche → **« Network Access »** → **« Add IP Address »** → **« Allow Access from Anywhere »** → confirme.

### 7.4. Récupérer la connection string
Menu de gauche → **« Database »** → bouton **« Connect »** sur ton cluster → **« Drivers »** → choisis **Python**, version 3.6 ou plus. Copie la chaîne qui ressemble à :
```
mongodb+srv://USERNAME:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
```

Remplace `<password>` par celui que tu as noté à l'étape 7.2 (sans les chevrons).

Colle dans `.env` sous `MONGO_URL`.

### 7.5. Insérer les témoignages de test
```bash
python seed/seed_mongo.py
```

Tu dois voir : `✅ Inserted 4 testimonials into Mongo.`

---

## 8. Lancer le projet en local

```bash
python app.py
```

Ouvre [http://localhost:5000](http://localhost:5000).

Vérifie :
- L'accueil s'affiche
- `/services` montre les 3 services publiés (issus de Postgres)
- `/temoignages` montre les 3 témoignages approuvés (issus de Mongo)
- `/admin/login` te demande tes identifiants (ceux de `.env` : `ADMIN_USERNAME` / `ADMIN_PASSWORD`)
- Une fois connecté à `/admin`, tu peux ajouter / modifier des services, modérer des témoignages

Pour arrêter : `Ctrl + C` dans le terminal.

---

## 9. Personnaliser : étape par étape

Comme pour le Projet 1, tu personnalises le site **sans toucher à la plomberie** : couleurs et polices (`static/css/variables.css`, ligne `@import` + variables), logo et images (`static/images/` — le site détecte automatiquement l'extension), nom du site (classe `Site` dans `app.py`). Puis :

### Étape 13 — Adapter tous les textes (lorem ipsum → ton contenu)

Méthode rapide avec une IA. **À faire page par page**, une à la fois, pour les **7 pages** :
`index.html`, `a-propos.html`, `services.html`, `galerie.html`, `contact.html`, `temoignages.html` et `mentions-legales.html`.

1. Ouvre une page, par exemple `templates/index.html`
2. Sélectionne tout son contenu (**Cmd + A** sur Mac, **Ctrl + A** sur Windows), puis copie (**Cmd + C** sur Mac, **Ctrl + C** sur Windows)
3. Va sur Claude ou ChatGPT, colle et demande (le **même prompt pour chaque page**) :
   > « Adapte ce code HTML pour le site d'un [ton sujet]. Garde **strictement** la même structure HTML et les mêmes balises Jinja2 (`{% extends %}`, `{% block %}`, `{{ ... }}`). Remplace uniquement les textes en français. Ton professionnel et chaleureux. »
4. Remplace tout le contenu de la page, puis sauvegarde
5. Recommence pour chaque page

> Pour `mentions-legales.html`, garde des **données cohérentes** avec ton sujet (l'avertissement « projet étudiant » est déjà en haut de la page).

### Étape 14 — Adapter les données de seed
Ouvre `seed/seed_postgres.py`. Remplace les listes `CATEGORIES` et `SERVICES` par ce qui correspond à ton sujet. Exemple pour un restaurant :

```python
CATEGORIES = [
    {"name": "Entrées", "slug": "entrees"},
    {"name": "Plats", "slug": "plats"},
    {"name": "Desserts", "slug": "desserts"},
]
```

Puis relance : `python seed/seed_postgres.py` (les anciennes données sont supprimées avant l'insertion).

Pareil pour `seed/seed_mongo.py` (témoignages).

> 💡 Astuce IA : copie tout le fichier de seed et demande à Claude / ChatGPT : « adapte ce fichier pour [ton sujet], même structure exactement ».

### Étape 15 — Adapter les libellés
- `templates/galerie.html` : renomme « Catégorie A/B/C ».
- `templates/temoignages.html` : adapte le texte d'intro.
- `app.py` (classe `Site`) : `name`, `tagline`, `description`.

---

## 10. Vérifier localement

Mêmes vérifications que le Projet 1 (responsive 320/768/1280 px, accessibilité clavier, Lighthouse ≥ 95) **plus** :

### Tests automatisés
```bash
python -m pytest -q
```
Tu dois voir `12 passed`.

### Admin
Connecte-toi sur `/admin/login`, crée un nouveau service, vérifie qu'il apparaît sur `/services`.

### Modération
Soumets un témoignage depuis `/temoignages`, va sur `/admin/testimonials`, clique sur **Publier**, retourne sur `/temoignages` : il apparaît.

---

## 11. Publier sur GitHub

```bash
git status
git add .
git commit -m "personnalisation : couleurs, données, textes"
git push
```

Conventions de message : `feat:`, `fix:`, `style:`, `docs:`.

---

## 12. Déployer sur Render

### 12.1. Créer le service
1. [dashboard.render.com](https://dashboard.render.com) → **« New + »** → **« Blueprint »**.
2. Connecte ton dépôt GitHub si pas déjà fait.
3. Sélectionne `mon-projet-2`. Render détecte `render.yaml` et propose la config → **« Apply »**.

### 12.2. Renseigner les variables d'environnement
Render te demande les `sync: false` (qu'il ne peut pas générer tout seul) :

| Variable | Valeur |
|---|---|
| `ADMIN_USERNAME` | celui de ton `.env` |
| `ADMIN_PASSWORD` | celui de ton `.env` |
| `DATABASE_URL` | celle de Neon |
| `MONGO_URL` | celle d'Atlas |

`FLASK_SECRET_KEY` est généré automatiquement par Render (`generateValue: true`).
`MONGO_DB_NAME` est déjà à `projet_2`.

Clique **« Apply »**.

### 12.3. Attendre le premier déploiement
2 à 5 minutes. Logs en direct. À la fin, ton URL apparaît : `https://mon-projet-2.onrender.com`.

### 12.4. Initialiser la BD distante
La BD Neon est vide tant que tu n'as pas joué le seed sur Render. Deux options :

**Option A — depuis ton ordi** : Le seed Postgres se lance depuis ta machine (puisque `DATABASE_URL` dans ton `.env` pointe sur Neon, distant) :
```bash
python seed/seed_postgres.py
python seed/seed_mongo.py
```

**Option B — Shell Render** : sur le service Render, onglet **« Shell »**, lance :
```bash
python seed/seed_postgres.py
python seed/seed_mongo.py
```

Une fois fait, recharge ton URL Render : les services et témoignages doivent apparaître.

> ⚠️ Si `/temoignages` affiche « MongoDB à configurer » alors que `MONGO_URL` est bien rempli : retourne sur Atlas → **Network Access** et vérifie que `0.0.0.0/0` est bien dans la whitelist.

---

## 13. Après déploiement

### 13.1. Mettre à jour `robots.txt` et `sitemap.xml`
Remplace `VOTRE-DOMAINE-RENDER.onrender.com` par ta vraie URL dans les deux fichiers de `static/`, puis :
```bash
git add static/robots.txt static/sitemap.xml
git commit -m "fix: vraie URL Render dans robots/sitemap"
git push
```
Render redéploie automatiquement.

### 13.2. Tester l'accessibilité et les perfs
Mêmes outils que pour le Projet 1 : [pagespeed.web.dev](https://pagespeed.web.dev), [accessibilitychecker.org](https://www.accessibilitychecker.org).

> ⚠️ **Render free tier** : le service se met en veille après 15 minutes d'inactivité. Le premier chargement après une veille prend 30 à 60 secondes. Normal sur le plan gratuit.

---

## 14. Workflow quotidien

```bash
source venv/bin/activate         # active le venv si nécessaire
python app.py                    # serveur local
# … tu modifies tes fichiers …
python -m pytest -q              # rejoue les tests
git add . && git commit -m "..."
git push                         # Render redéploie tout seul
```

Bon code !
