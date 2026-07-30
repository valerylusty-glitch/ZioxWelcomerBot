"""
database/warnings.py

Gestion des avertissements.
"""

from .connection import get_db


# ======================================================
# TABLE
# ======================================================

async def initialize_warnings():

    async with await get_db() as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS warnings(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            chat_id INTEGER NOT NULL,

            user_id INTEGER NOT NULL,

            admin_id INTEGER NOT NULL,

            reason TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)

        await db.commit()


# ======================================================
# AJOUTER UN WARN
# ======================================================

async def add_warning(
    chat_id: int,
    user_id: int,
    admin_id: int,
    reason: str,
):

    async with await get_db() as db:

        await db.execute("""
        INSERT INTO warnings(
            chat_id,
            user_id,
            admin_id,
            reason
        )
        VALUES(?,?,?,?)
        """, (
            chat_id,
            user_id,
            admin_id,
            reason,
        ))

        await db.commit()


# ======================================================
# NOMBRE DE WARNS
# ======================================================

async def count_warnings(
    chat_id: int,
    user_id: int,
):

    async with await get_db() as db:

        cursor = await db.execute("""
        SELECT COUNT(*)
        FROM warnings
        WHERE chat_id=?
        AND user_id=?
        """, (
            chat_id,
            user_id,
        ))

        result = await cursor.fetchone()

        return result[0]


# ======================================================
# SUPPRIMER LES WARNS
# ======================================================

async def clear_warnings(
    chat_id: int,
    user_id: int,
):

    async with await get_db() as db:

        await db.execute("""
        DELETE FROM warnings
        WHERE chat_id=?
        AND user_id=?
        """, (
            chat_id,
            user_id,
        ))

        await db.commit()
