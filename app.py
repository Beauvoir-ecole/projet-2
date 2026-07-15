"""Flask application — Projet 2, full-stack site (front + back).

Architecture (MVC):
  - Model       : ``models/`` (SQLAlchemy for Postgres, PyMongo for Mongo).
  - View        : Jinja2 templates in ``templates/``.
  - Controller  : routes registered in this module.
"""
import os
import ssl
from datetime import datetime
from functools import wraps
from urllib.parse import urlsplit, urlunsplit

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)

from models import (
    CategoryRepository,
    ServiceRepository,
    TestimonialRepository,
    db,
)
from sqlalchemy.exc import SQLAlchemyError
from pymongo.errors import PyMongoError

load_dotenv()

app = Flask(__name__)

# Debug mode auto-detects the environment: ON in local development, OFF in
# production. Render sets FLASK_ENV=production (see render.yaml); locally the
# variable is unset, so we default to development. This single flag drives both
# the runtime and the pedagogical progress notifier (hidden in production).
app.debug = os.environ.get("FLASK_ENV", "development") != "production"

app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-only-do-not-use")


def normalize_database_url(raw_url: str) -> str:
    """Return a SQLAlchemy URL that uses the pure-Python ``pg8000`` driver.

    Neon (and most Postgres providers) hand out a URL of the form
    ``postgresql://user:password@host/db?sslmode=require``. By default SQLAlchemy
    would try to load the compiled ``psycopg2`` driver, which fails to install
    on some machines and on Render. We rewrite the scheme to
    ``postgresql+pg8000`` (no compilation, works everywhere) and drop the
    ``sslmode`` query argument — pg8000 doesn't read it; SSL is configured on
    the engine instead (see ``engine_options_for``). The student can paste the
    Neon URL into ``.env`` unchanged: this happens transparently.
    """
    parts = urlsplit(raw_url)
    if parts.scheme in ("postgres", "postgresql", "postgresql+psycopg2"):
        parts = parts._replace(scheme="postgresql+pg8000", query="")
        return urlunsplit(parts)
    return raw_url


def engine_options_for(database_url: str) -> dict:
    """Enable TLS for hosted Postgres. pg8000 expects an ``ssl.SSLContext``.

    A default context verifies the certificate and sends SNI (required by
    Neon to route the connection). SQLite (local dev and tests) needs no
    options.
    """
    if database_url.startswith("postgresql+pg8000://"):
        return {"connect_args": {"ssl_context": ssl.create_default_context()}}
    return {}


_database_url = normalize_database_url(os.environ.get("DATABASE_URL", "sqlite:///dev.db"))
app.config["SQLALCHEMY_DATABASE_URI"] = _database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = engine_options_for(_database_url)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# ---------------------------------------------------------------------------
# Site metadata (Model layer — shared with every template)
# ---------------------------------------------------------------------------
class Site:
    """Site-wide metadata exposed to every template."""

    def __init__(self) -> None:
        self.name = "Lorem Ipsum"
        self.tagline = "Lorem ipsum dolor sit amet, consectetur adipiscing elit"
        self.description = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        )
        self.year = datetime.now().year
        self.pages = [
            {"endpoint": "home", "url": "/", "label": "Accueil"},
            {"endpoint": "about", "url": "/a-propos", "label": "À propos"},
            {"endpoint": "services", "url": "/services", "label": "Services"},
            {"endpoint": "gallery", "url": "/galerie", "label": "Galerie"},
            {"endpoint": "testimonials", "url": "/temoignages", "label": "Témoignages"},
            {"endpoint": "contact", "url": "/contact", "label": "Contact"},
        ]


SITE = Site()

# Repositories are stateless — instantiated once and reused everywhere.
categories_repo = CategoryRepository()
services_repo = ServiceRepository()
testimonials_repo = TestimonialRepository()


# ---------------------------------------------------------------------------
# Helpers exposed to templates
# ---------------------------------------------------------------------------
def find_image(name: str, folder: str = "images") -> str:
    """Return the URL of the first existing image whose stem matches ``name``."""
    extensions = ("webp", "jpg", "jpeg", "png", "avif", "svg")
    base_dir = os.path.join(app.static_folder, folder)
    for ext in extensions:
        candidate = f"{name}.{ext}"
        if os.path.exists(os.path.join(base_dir, candidate)):
            return url_for("static", filename=f"{folder}/{candidate}")
    return url_for("static", filename=f"{folder}/{name}.svg")


CUSTOMIZATIONS_FILE = "css/customizations.css"
CUSTOMIZATION_MARKER = "/* CUSTOMIZED */"


def is_site_customized() -> bool:
    path = os.path.join(app.static_folder, CUSTOMIZATIONS_FILE)
    if not os.path.exists(path):
        return False
    with open(path, "r", encoding="utf-8") as handle:
        return CUSTOMIZATION_MARKER in handle.read()


@app.context_processor
def inject_globals():
    return {
        "site": SITE,
        "find_image": find_image,
        "is_customized": is_site_customized(),
        "is_admin": session.get("is_admin", False),
        "is_debug": app.debug,
    }


# ---------------------------------------------------------------------------
# Pedagogical progress tracker (visible in dev mode only)
# ---------------------------------------------------------------------------
def _file_contains(relative_path: str, needle: str) -> bool:
    full = os.path.join(os.path.dirname(__file__), relative_path)
    try:
        with open(full, encoding="utf-8") as handle:
            return needle in handle.read()
    except FileNotFoundError:
        return False


def _env_value(name: str) -> str:
    """Read a variable straight from the ``.env`` file (not ``os.environ``).

    The progress tracker must reflect what the student just typed into
    ``.env`` after a simple page refresh — without restarting the server
    (``os.environ`` is only loaded once, at startup). Returns "" if the
    file or the key is absent.
    """
    path = os.path.join(os.path.dirname(__file__), ".env")
    try:
        with open(path, encoding="utf-8") as handle:
            for raw in handle:
                line = raw.strip()
                if line.startswith(f"{name}="):
                    return line.split("=", 1)[1].strip()
    except FileNotFoundError:
        return ""
    return ""


def _is_configured(value: str) -> bool:
    """True when a ``.env`` value is real, i.e. set and not an example value."""
    if not value:
        return False
    placeholders = ("user:password", "@host/", "@cluster.mongodb.net", "change-me")
    return not any(token in value for token in placeholders)


PROGRESS_STEPS = [
    {
        "title": "Créer ton fichier .env",
        "file": ".env",
        "action": (
            "1. Copie <code>.env.example</code> vers <code>.env</code> "
            "(<code>cp .env.example .env</code>).\n"
            "2. Génère une clé secrète avec "
            "<code>python -c \"import secrets; print(secrets.token_hex(32))\"</code> "
            "et colle-la dans <code>FLASK_SECRET_KEY</code>.\n"
            "3. Change aussi <code>ADMIN_PASSWORD</code> par un mot de passe fort."
        ),
        "done": lambda: os.path.exists(os.path.join(os.path.dirname(__file__), ".env")),
    },
    {
        "title": "Versionner ton projet sur GitHub",
        "file": "(terminal Git)",
        "action": (
            "1. Initialise le dépôt à la racine du projet : <code>git init</code>.\n"
            "2. Crée un dépôt vide sur "
            "<a href=\"https://github.com/new\" target=\"_blank\" rel=\"noopener\">github.com/new</a> "
            "(ne coche pas « Add a README »), puis relie-le :\n"
            "<code>git remote add origin https://github.com/TON-PSEUDO/ton-projet.git</code>.\n"
            "3. Premier envoi :\n"
            "<code>git add .</code>\n"
            "<code>git commit -m \"première version\"</code>\n"
            "<code>git branch -M main</code>\n"
            "<code>git push -u origin main</code>.\n"
            "Détails pas-à-pas dans <code>deploiement.md</code> (§3 et §11)."
        ),
        "done": lambda: os.path.isdir(os.path.join(os.path.dirname(__file__), ".git")),
    },
    {
        "title": "Activer le garde-fou anti-secret",
        "file": "(terminal Git)",
        "action": (
            "Ce projet manipule des secrets (clé Flask, mots de passe, URL de bases "
            "de données). Un script bloque automatiquement tout commit qui en "
            "contiendrait.\n"
            "Active-le une fois (à refaire après chaque nouveau clone) :\n"
            "<code>git config core.hooksPath hooks</code>.\n"
            "Ton fichier <code>.env</code>, lui, n'est jamais envoyé sur GitHub : "
            "il est déjà listé dans <code>.gitignore</code>."
        ),
        "done": lambda: _file_contains(".git/config", "hooksPath"),
    },
    {
        "title": "Connecter PostgreSQL (Neon)",
        "file": ".env",
        "action": (
            "1. Crée un projet sur <a href=\"https://neon.tech\" target=\"_blank\" rel=\"noopener\">neon.tech</a>.\n"
            "2. Copie la connection string et colle-la dans <code>DATABASE_URL</code> "
            "du fichier <code>.env</code> (garde-la telle quelle, le projet adapte "
            "le driver tout seul).\n"
            "3. Lance <code>python seed/seed_postgres.py</code>.\n"
            "4. <strong>Relance le serveur pour qu'il voie ta base</strong> : "
            "dans le terminal, fais <code>Ctrl+C</code> puis <code>python app.py</code>. "
            "(Sans ça, le site continue d'afficher l'ancienne version : changer "
            "<code>.env</code> oblige toujours à relancer.)"
        ),
        "done": lambda: _is_configured(_env_value("DATABASE_URL")),
    },
    {
        "title": "Connecter MongoDB Atlas",
        "file": ".env",
        "action": (
            "1. Crée un cluster M0 gratuit sur "
            "<a href=\"https://cloud.mongodb.com\" target=\"_blank\" rel=\"noopener\">cloud.mongodb.com</a>.\n"
            "2. <strong>Ajoute <code>0.0.0.0/0</code> dans Network Access</strong> "
            "(sinon Render ne pourra pas se connecter).\n"
            "3. Colle la connection string dans <code>MONGO_URL</code> de ton <code>.env</code>.\n"
            "4. Lance <code>python seed/seed_mongo.py</code>.\n"
            "5. <strong>Relance le serveur pour qu'il voie ta base</strong> : "
            "dans le terminal, fais <code>Ctrl+C</code> puis <code>python app.py</code>."
        ),
        "done": lambda: _is_configured(_env_value("MONGO_URL")),
    },
    {
        "title": "Personnaliser la mise en page (bouton ✨)",
        "file": "(bouton ✨ Personnalise-moi, en bas à droite)",
        "action": (
            "1. Clique sur le bouton <strong>✨ Personnalise-moi</strong> "
            "en bas à droite de la page.\n"
            "2. Réponds aux questions (position du héros, alignements, "
            "style des cartes…) puis valide.\n"
            "Ta mise en page s'adapte toute seule, et le bouton disparaît "
            "une fois la personnalisation enregistrée."
        ),
        "done": is_site_customized,
    },
    {
        "title": "Changer les couleurs",
        "file": "static/css/variables.css",
        "action": (
            "1. Ouvre <code>static/css/variables.css</code>.\n"
            "2. Remplace <code>--primary-color: #2563eb</code> "
            "et <code>--secondary-color: #f59e0b</code> par tes couleurs."
        ),
        "done": lambda: not _file_contains("static/css/variables.css", "#2563eb"),
    },
    {
        "title": "Changer les polices",
        "file": "static/css/variables.css",
        "action": (
            "1. Choisis 2 polices sur <a href=\"https://fonts.google.com\" target=\"_blank\" rel=\"noopener\">fonts.google.com</a>.\n"
            "2. Ouvre <code>static/css/variables.css</code> (tout se passe dans ce seul fichier).\n"
            "3. Remplace les noms <code>Playfair Display</code> et <code>Inter</code> "
            "dans la ligne <code>@import</code> tout en haut.\n"
            "4. Remplace-les aussi dans <code>--font-title</code> et <code>--font-body</code>."
        ),
        "done": lambda: not _file_contains("static/css/variables.css", "Playfair Display"),
    },
    {
        "title": "Remplacer le logo",
        "file": "static/images/logo.svg",
        "action": (
            "1. Mets ton fichier logo dans le dossier <code>static/images/</code> "
            "et nomme-le <code>logo.png</code> (ou <code>logo.jpg</code>).\n"
            "2. Supprime l'ancien fichier <code>static/images/logo.svg</code> "
            "(celui qui affiche « VOTRE LOGO »).\n"
            "Astuce : si ton logo est déjà en .svg, remplace directement "
            "<code>logo.svg</code> — dans ce cas rien à supprimer."
        ),
        "done": lambda: not _file_contains("static/images/logo.svg", "VOTRE LOGO"),
    },
    {
        "title": "Remplacer image_1, image_2, image_3",
        "file": "static/images/",
        "action": (
            "Remplace <code>image_1.svg</code>, <code>image_2.svg</code> "
            "et <code>image_3.svg</code>\n"
            "par tes propres images (JPG/WebP/PNG OK)."
        ),
        "done": lambda: (
            not _file_contains("static/images/image_1.svg", "image_1.svg — à remplacer")
            and not _file_contains("static/images/image_2.svg", "image_2.svg — à remplacer")
            and not _file_contains("static/images/image_3.svg", "image_3.svg — à remplacer")
        ),
    },
    {
        "title": "Remplacer les images de la galerie",
        "file": "static/images/galerie/",
        "action": (
            "Remplace les 6 fichiers <code>img-1.svg</code> à <code>img-6.svg</code>\n"
            "dans <code>static/images/galerie/</code> par tes propres images."
        ),
        "done": lambda: not _file_contains("static/images/galerie/img-1.svg", "img-1.svg"),
    },
    {
        "title": "Adapter les données de seed PostgreSQL",
        "file": "seed/seed_postgres.py",
        "action": (
            "1. Ouvre <code>seed/seed_postgres.py</code>.\n"
            "2. Remplace les listes <code>CATEGORIES</code> et <code>SERVICES</code> "
            "par tes vraies données.\n"
            "3. Relance <code>python seed/seed_postgres.py</code>."
        ),
        "done": lambda: not _file_contains("seed/seed_postgres.py", '"Catégorie A"'),
    },
    {
        "title": "Adapter les témoignages de seed Mongo",
        "file": "seed/seed_mongo.py",
        "action": (
            "1. Ouvre <code>seed/seed_mongo.py</code>.\n"
            "2. Remplace la liste <code>TESTIMONIALS</code> par des témoignages "
            "cohérents avec ton sujet.\n"
            "3. Relance <code>python seed/seed_mongo.py</code>."
        ),
        "done": lambda: not _file_contains("seed/seed_mongo.py", "Lorem ipsum dolor sit amet"),
    },
    {
        "title": "Renommer les catégories de la galerie",
        "file": "templates/galerie.html",
        "action": (
            "1. Ouvre <code>templates/galerie.html</code>.\n"
            "2. Va aux <strong>lignes 19 à 21</strong> : remplace « Catégorie A/B/C » "
            "par tes vraies catégories.\n"
            "Attention : garde les <code>data-category=\"a/b/c\"</code>."
        ),
        "done": lambda: not _file_contains("templates/galerie.html", "Catégorie A"),
    },
    {
        "title": "Coller ton lien Tally (contact)",
        "file": "templates/contact.html",
        "action": (
            "1. Crée ton formulaire sur <a href=\"https://tally.so\" target=\"_blank\" rel=\"noopener\">tally.so</a>.\n"
            "2. Remplace <code>REMPLACE_PAR_TON_LIEN_TALLY</code> "
            "dans <code>templates/contact.html</code>."
        ),
        "done": lambda: not _file_contains("templates/contact.html", "REMPLACE_PAR_TON_LIEN_TALLY"),
    },
    {
        "title": "Adapter le nom du site",
        "file": "app.py",
        "action": (
            "Dans <code>app.py</code>, classe <code>Site</code> "
            "(vers la <strong>ligne 96</strong>) :\n"
            "1. <code>self.name</code> : remplace <code>\"Lorem Ipsum\"</code> "
            "par le vrai nom de ton site.\n"
            "2. <code>self.tagline</code> : remplace le texte "
            "par ton slogan.\n"
            "3. <code>self.description</code> : remplace les 2 phrases "
            "par une description de ton site."
        ),
        "done": lambda: SITE.name != "Lorem Ipsum",
    },
    {
        "title": "Adapter tous les textes (lorem ipsum) avec une IA",
        "file": "templates/ : index, a-propos, services, galerie, contact, temoignages, mentions-legales",
        "action": (
            "À faire <strong>page par page</strong>, une à la fois. "
            "Les 7 pages à adapter : <code>index.html</code>, <code>a-propos.html</code>, "
            "<code>services.html</code>, <code>galerie.html</code>, <code>contact.html</code>, "
            "<code>temoignages.html</code> et <code>mentions-legales.html</code>.\n"
            "1. Ouvre une page dans <code>templates/</code>.\n"
            "2. Sélectionne tout (<strong>Cmd+A</strong> sur Mac, <strong>Ctrl+A</strong> sur Windows), "
            "puis copie (<strong>Cmd+C</strong> sur Mac, <strong>Ctrl+C</strong> sur Windows).\n"
            "3. Colle dans <a href=\"https://claude.ai\" target=\"_blank\" rel=\"noopener\">Claude</a> "
            "ou ChatGPT avec ce message :\n"
            "« Voici une page HTML qui contient du Jinja2. Remplace tous les textes "
            "en lorem ipsum par du vrai contenu pour un site de [TON SUJET]. "
            "Ne change pas les balises ni le code entre {{ }} et {% %}. »\n"
            "4. Recopie la réponse dans ton fichier, puis sauvegarde.\n"
            "5. Recommence pour chaque page.\n"
            "Cas particulier <code>mentions-legales.html</code> : mets tes vraies "
            "coordonnées (ou des données fictives cohérentes avec ton sujet)."
        ),
        "done": lambda: (
            not _file_contains("templates/index.html", "Lorem ipsum dolor sit amet")
            and not _file_contains("templates/mentions-legales.html", "Lorem Ipsum SAS")
        ),
    },
    {
        "title": "Déployer sur Render, puis finaliser robots.txt / sitemap.xml",
        "file": "static/robots.txt et static/sitemap.xml",
        "action": (
            "1. Pousse ton travail sur GitHub (<code>git add . && git commit -m \"...\" "
            "&& git push</code>).\n"
            "2. Sur <a href=\"https://dashboard.render.com\" target=\"_blank\" rel=\"noopener\">Render</a> : "
            "<strong>New + → Blueprint</strong>, choisis ton dépôt (Render lit "
            "<code>render.yaml</code>), puis renseigne les variables "
            "<code>ADMIN_USERNAME</code>, <code>ADMIN_PASSWORD</code>, "
            "<code>DATABASE_URL</code>, <code>MONGO_URL</code>.\n"
            "3. Une fois en ligne, remplace "
            "<code>VOTRE-DOMAINE-RENDER.onrender.com</code> par ta vraie URL Render "
            "dans <code>static/robots.txt</code> et <code>static/sitemap.xml</code>, "
            "puis commit + push.\n"
            "Procédure complète dans <code>deploiement.md</code> (§12 et §13)."
        ),
        "done": lambda: not _file_contains("static/robots.txt", "VOTRE-DOMAINE-RENDER"),
    },
]


def current_progress_step():
    for index, step in enumerate(PROGRESS_STEPS):
        try:
            if not step["done"]():
                return {
                    "index": index + 1,
                    "total": len(PROGRESS_STEPS),
                    "title": step["title"],
                    "file": step["file"],
                    "action": step["action"],
                }
        except Exception:
            continue
    return None


@app.route("/api/progress")
def api_progress():
    if not app.debug:
        abort(404)
    step = current_progress_step()
    return jsonify(step or {"done": True, "total": len(PROGRESS_STEPS)})


# ---------------------------------------------------------------------------
# Graceful database failure (lets the site boot without Postgres or Mongo)
# ---------------------------------------------------------------------------
def render_db_missing(kind: str):
    """Render the friendly 'database not configured' page."""
    return render_template("db_missing.html", kind=kind), 503


# ---------------------------------------------------------------------------
# Authentication helper (server-side security)
# ---------------------------------------------------------------------------
def admin_required(view):
    """Restrict a route to authenticated admins."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


# ---------------------------------------------------------------------------
# Public routes (Controllers)
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html", current_page="home")


@app.route("/a-propos")
def about():
    return render_template("a-propos.html", current_page="about")


@app.route("/services")
def services():
    try:
        items = services_repo.list_published()
    except SQLAlchemyError:
        return render_db_missing("postgres")
    return render_template("services.html", current_page="services", services=items)


@app.route("/galerie")
def gallery():
    return render_template("galerie.html", current_page="gallery")


@app.route("/temoignages", methods=["GET", "POST"])
def testimonials():
    if request.method == "POST":
        try:
            testimonials_repo.create(
                author=request.form.get("author", ""),
                comment=request.form.get("comment", ""),
                rating=request.form.get("rating", 0),
            )
            flash("Merci ! Ton témoignage sera publié après validation.", "success")
        except ValueError as error:
            flash(str(error), "error")
        except (PyMongoError, RuntimeError):
            return render_db_missing("mongo")
        return redirect(url_for("testimonials"))

    try:
        items = testimonials_repo.list_approved()
    except (PyMongoError, RuntimeError):
        return render_db_missing("mongo")
    return render_template(
        "temoignages.html", current_page="testimonials", testimonials=items
    )


@app.route("/contact")
def contact():
    return render_template("contact.html", current_page="contact")


@app.route("/mentions-legales")
def legal():
    return render_template("mentions-legales.html", current_page="legal")


# ---------------------------------------------------------------------------
# Admin routes
# ---------------------------------------------------------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        expected_user = os.environ.get("ADMIN_USERNAME", "admin")
        expected_pass = os.environ.get("ADMIN_PASSWORD", "")
        if username == expected_user and password and password == expected_pass:
            session["is_admin"] = True
            # Ne suivre `next` que s'il pointe vers un chemin interne
            # (evite un open redirect vers un site externe).
            next_url = request.args.get("next", "")
            if not next_url.startswith("/") or next_url.startswith("//"):
                next_url = url_for("admin_dashboard")
            return redirect(next_url)
        flash("Identifiants invalides.", "error")
    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("home"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    counts = {"services": None, "categories": None, "testimonials": None}
    try:
        counts["services"] = len(services_repo.list_all())
        counts["categories"] = len(categories_repo.list_all())
    except SQLAlchemyError:
        pass
    try:
        counts["testimonials"] = len(testimonials_repo.list_all())
    except (PyMongoError, RuntimeError):
        pass
    return render_template("admin/dashboard.html", counts=counts)


@app.route("/admin/services")
@admin_required
def admin_services():
    return render_template(
        "admin/services.html",
        services=services_repo.list_all(),
        categories=categories_repo.list_all(),
    )


@app.route("/admin/services/new", methods=["GET", "POST"])
@admin_required
def admin_service_create():
    if request.method == "POST":
        try:
            services_repo.create(
                title=request.form.get("title", ""),
                description=request.form.get("description", ""),
                category_id=int(request.form.get("category_id", 0)),
                is_published=bool(request.form.get("is_published")),
            )
            flash("Service créé.", "success")
            return redirect(url_for("admin_services"))
        except ValueError as error:
            flash(str(error), "error")
    return render_template(
        "admin/service_form.html",
        service=None,
        categories=categories_repo.list_all(),
    )


@app.route("/admin/services/<int:service_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_service_edit(service_id: int):
    service = services_repo.get(service_id)
    if service is None:
        abort(404)
    if request.method == "POST":
        try:
            services_repo.update(
                service_id,
                title=request.form.get("title", ""),
                description=request.form.get("description", ""),
                category_id=int(request.form.get("category_id", 0)),
                is_published=bool(request.form.get("is_published")),
            )
            flash("Service mis à jour.", "success")
            return redirect(url_for("admin_services"))
        except ValueError as error:
            flash(str(error), "error")
    return render_template(
        "admin/service_form.html",
        service=service,
        categories=categories_repo.list_all(),
    )


@app.route("/admin/services/<int:service_id>/delete", methods=["POST"])
@admin_required
def admin_service_delete(service_id: int):
    services_repo.delete(service_id)
    flash("Service supprimé.", "success")
    return redirect(url_for("admin_services"))


@app.route("/admin/testimonials")
@admin_required
def admin_testimonials():
    return render_template(
        "admin/testimonials.html",
        testimonials=testimonials_repo.list_all(),
    )


@app.route("/admin/testimonials/<testimonial_id>/toggle", methods=["POST"])
@admin_required
def admin_testimonial_toggle(testimonial_id: str):
    current = testimonials_repo.get(testimonial_id)
    if current is None:
        abort(404)
    testimonials_repo.set_approved(testimonial_id, approved=not current.is_approved)
    return redirect(url_for("admin_testimonials"))


@app.route("/admin/testimonials/<testimonial_id>/delete", methods=["POST"])
@admin_required
def admin_testimonial_delete(testimonial_id: str):
    testimonials_repo.delete(testimonial_id)
    flash("Témoignage supprimé.", "success")
    return redirect(url_for("admin_testimonials"))


# ---------------------------------------------------------------------------
# Customizer API (kept from Projet 1)
# ---------------------------------------------------------------------------
def build_customization_css(answers: dict) -> str:
    rules: list[str] = []

    hero = answers.get("hero")
    if hero == "left":
        rules.append(
            "@media (min-width: 768px) { .hero-content { flex-direction: row-reverse; } }"
        )
    elif hero == "right":
        rules.append(
            "@media (min-width: 768px) { .hero-content { flex-direction: row; } }"
        )

    text_align = answers.get("textAlign")
    if text_align in {"left", "center", "justify"}:
        rules.append(f"main p {{ text-align: {text_align}; }}")

    title_align = answers.get("titleAlign")
    if title_align in {"left", "center"}:
        rules.append(f"main h1, main h2 {{ text-align: {title_align}; }}")

    corners = answers.get("corners")
    if corners == "square":
        rules.append(
            ".card, .btn, .filter-btn, .gallery-item, "
            ".hero-image img, .two-col img, .legal-content img "
            "{ border-radius: 0; }"
        )

    nav_align = answers.get("navAlign")
    if nav_align == "center":
        rules.append(
            "@media (min-width: 768px) { .header-inner { justify-content: space-around; } }"
        )
    elif nav_align == "left":
        rules.append(
            "@media (min-width: 768px) { .header-inner { justify-content: flex-start; gap: var(--space-xl); } }"
        )

    cta_align = answers.get("ctaAlign")
    if cta_align == "center":
        rules.append(
            ".hero .btn { display: block; margin-left: auto; margin-right: auto; width: max-content; }"
        )
    elif cta_align == "right":
        rules.append(".hero .btn { display: block; margin-left: auto; width: max-content; }")

    cards = answers.get("cards")
    if cards == "flat":
        rules.append(".card { box-shadow: none; border-top-width: 1px; }")
        rules.append(".card:hover { box-shadow: none; transform: none; }")
    elif cards == "outlined":
        rules.append(
            ".card { box-shadow: none; border: 2px solid var(--primary-color);"
            " border-top: 4px solid var(--secondary-color); }"
        )

    footer_align = answers.get("footerAlign")
    if footer_align == "center":
        rules.append(
            ".footer-inner { text-align: center; }"
            " .footer-inner ul { align-items: center; }"
            " .footer-inner nav ul { display: flex; flex-direction: column; gap: var(--space-xs); }"
        )

    body = "\n".join(rules) if rules else "/* No customization rules. */"
    return f"{CUSTOMIZATION_MARKER}\n/* Auto-generated. Re-run the quiz to overwrite. */\n\n{body}\n"


@app.route("/api/customize", methods=["POST"])
def api_customize():
    answers = request.get_json(silent=True) or {}
    css = build_customization_css(answers)
    path = os.path.join(app.static_folder, CUSTOMIZATIONS_FILE)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(css)
    return jsonify({"status": "ok"})


# ---------------------------------------------------------------------------
# SEO static files & error handlers
# ---------------------------------------------------------------------------
@app.route("/robots.txt")
def robots():
    return send_from_directory(app.static_folder, "robots.txt")


@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(app.static_folder, "sitemap.xml")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # debug is taken from app.debug above (auto: on locally, off in production).
    app.run(port=5000)
