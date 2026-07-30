"""
database/groups.py

Gestion des groupes.
"""

from .connection import get_db


async def initialize_groups():
    """
    Création de la table groups.
    """

    async with await get_db() as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS groups(

            chat_id INTEGER PRIMARY KEY,

            title TEXT,

            language TEXT DEFAULT 'fr',

            welcome_enabled INTEGER DEFAULT 1,
            goodbye_enabled INTEGER DEFAULT 1,
            captcha_enabled INTEGER DEFAULT 0,

            welcome_message TEXT DEFAULT '👋 Bienvenue {user} sur {group} !',

            goodbye_message TEXT DEFAULT '👋 {user} a quitté le groupe.',

            rules TEXT DEFAULT '',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)

        await db.commit()
