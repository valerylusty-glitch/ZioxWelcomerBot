"""
Script de démarrage : lance le bot Telegram ET l'API Flask en parallèle.
Utilisé par le Dockerfile pour Railway.
"""
import os
import sys
import threading
from dotenv import load_dotenv

load_dotenv()

# Ajouter les dossiers au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "bot"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "api"))


def lancer_api():
    """Lance l'API Flask dans un thread."""
    from api.server import app
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, use_reloader=False)


def lancer_bot():
    """Lance le bot Telegram dans un thread."""
    from bot.main import main as bot_main
    bot_main()


if __name__ == "__main__":
    print("Démarrage de Ziox...")

    # Initialiser la base de données une seule fois
    from database import init_db
    init_db()
    print("Base de données initialisée.")

    # Lancer l'API Flask en arrière-plan
    api_thread = threading.Thread(target=lancer_api, daemon=True)
    api_thread.start()
    print(f"API Flask lancée sur le port {os.getenv('PORT', 8080)}")

    # Lancer le bot Telegram (bloquant)
    print("Lancement du bot Telegram...")
    lancer_bot()
