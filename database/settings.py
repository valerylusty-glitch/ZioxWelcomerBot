"""
database/settings.py

Paramètres avancés des groupes.
"""

from .connection import get_db


# ======================================================
# TABLE
# ======================================================

async def initialize_settings():

    async with await get_db() as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS settings(

            chat_id INTEGER,

            key TEXT,

            value TEXT,

            PRIMARY KEY(chat_id,key)

        )
        """)

        await db.commit()


# ======================================================
# CRUD
# ======================================================

async def set_setting(
    chat_id: int,
    key: str,
    value: str,
):

    async with await get_db() as db:

        await db.execute("""
        INSERT OR REPLACE INTO settings(
            chat_id,
            key,
            value
        )
        VALUES(?,?,?)
        """, (
            chat_id,
            key,
            value,
        ))

        await db.commit()


async def get_setting(
    chat_id: int,
    key: str,
):

    async with await get_db() as db:

        cursor = await db.execute("""
        SELECT value
        FROM settings
        WHERE chat_id=?
        AND key=?
        """, (
            chat_id,
            key,
        ))

        result = await cursor.fetchone()

        if result:
            return result["value"]

        return None
