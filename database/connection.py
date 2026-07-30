"""
database/connection.py

Gestion de la connexion SQLite.
"""

# ======================================================
# IMPORTS
# ======================================================

import aiosqlite

from config import DATABASE_PATH


# ======================================================
# CONNEXION
# ======================================================

async def get_db():
    """
    Retourne une connexion SQLite configurée.
    """

    db = await aiosqlite.connect(DATABASE_PATH)

    db.row_factory = aiosqlite.Row

    return db
