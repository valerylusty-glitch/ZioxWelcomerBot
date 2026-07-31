"""
Script de démarrage : lance le bot Telegram ET l'API Flask en parallèle.
Utilisé par le Dockerfile pour Railway.
"""
import os
import sys
import threading
from dotenv import load_dotenv

# Ajouter le dossier bot/ au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "bot"))

load_dotenv()


def lancer_api():
    """Lance l'API Flask dans un thread."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "api"))
    # Importer et lancer Flask
    from server import app
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, use_reloader=False)


def lancer_bot():
    """Lance le bot Telegram dans un thread."""
    from main import main as bot_main
    bot_main()


if __name__ == "__main__":
    print("Démarrage de Ziox...")

    # Lancer l'API Flask en arrière-plan
    api_thread = threading.Thread(target=lancer_api, daemon=True)
    api_thread.start()
    print("API Flask lancée sur le port", os.getenv("PORT", 8080))

    # Lancer le bot Telegram (bloquant)
    print("Lancement du bot Telegram...")
    lancer_bot()
