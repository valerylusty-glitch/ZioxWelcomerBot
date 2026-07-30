"""
bot.py

Point d'entrée principal de ZioxWelcomer.
"""

# ======================================================
# IMPORTS
# ======================================================

import asyncio
import logging

from telegram.ext import Application

from config import BOT_TOKEN, LOG_LEVEL
from database import database
from handlers import register_handlers


# ======================================================
# LOGS
# ======================================================

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
)

logger = logging.getLogger("ZioxWelcomer")


# ======================================================
# INITIALISATION
# ======================================================

async def initialize():
    """
    Initialise la base de données.
    """
    logger.info("Initialisation de la base de données...")
    await database.initialize()
    logger.info("Base de données prête.")


# ======================================================
# APPLICATION
# ======================================================

def create_application() -> Application:
    """
    Crée l'application Telegram.
    """
    app = Application.builder().token(BOT_TOKEN).build()

register_handlers(app)

return app


# ======================================================
# MAIN
# ======================================================

async def main():
    """
    Démarrage du bot.
    """

    await initialize()

    app = create_application()

    logger.info("ZioxWelcomer est démarré.")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # Garde le bot actif
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot arrêté.")
