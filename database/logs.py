"""
database/logs.py

Gestion des logs.
"""

from .connection import get_db


# ======================================================
# TABLE
# ======================================================

async def initialize_logs():

    async with await get_db() as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS logs(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            chat_id INTEGER,

            user_id INTEGER,

            action TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)

        await db.commit()


# ======================================================
# CRUD
# ======================================================

async def add_log(
    chat_id: int,
    user_id: int,
    action: str,
):

    async with await get_db() as db:

        await db.execute("""
        INSERT INTO logs(
            chat_id,
            user_id,
            action
        )
        VALUES(?,?,?)
        """, (
            chat_id,
            user_id,
            action,
        ))

        await db.commit()
