import os
from pathlib import Path

from dotenv import load_dotenv

# Racine du projet
BASE_DIR = Path(__file__).resolve().parent

# Charger les variables d'environnement
load_dotenv(BASE_DIR / ".env")

# ==========================
# Informations du bot
# ==========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = os.getenv("BOT_NAME", "ZioxWelcomer")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# ==========================
# Base de données
# ==========================

DATABASE_NAME = os.getenv("DATABASE_NAME", "ziox.db")
DATABASE_PATH = BASE_DIR / "data" / DATABASE_NAME

# ==========================
# Logs
# ==========================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOGS_DIR = BASE_DIR / "logs"

# ==========================
# Langue
# ==========================

LANGUAGE = os.getenv("LANGUAGE", "fr")

# ==========================
# Création des dossiers
# ==========================

(BASE_DIR / "data").mkdir(exist_ok=True)
(BASE_DIR / "logs").mkdir(exist_ok=True)
(BASE_DIR / "assets").mkdir(exist_ok=True)

# ==========================
# Vérifications
# ==========================

if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN introuvable ! "
        "Crée un fichier .env à partir de .env.example et ajoute ton token."
    )
