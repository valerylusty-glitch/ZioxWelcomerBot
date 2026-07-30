"""
database/members.py

Gestion des membres.
"""

# ======================================================
# IMPORTS
# ======================================================

from .connection import get_db


# ======================================================
# TABLE
# ======================================================

async def initialize_members():

    async with await get_db() as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS members(

            user_id INTEGER,

            chat_id INTEGER,

            username TEXT,

            first_name TEXT,

            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            PRIMARY KEY(user_id, chat_id)

        )
        """)

        await db.commit()


# ======================================================
# CRUD
# ======================================================

async def add_member(
    chat_id: int,
    user_id: int,
    username: str | None,
    first_name: str,
):

    async with await get_db() as db:

        await db.execute("""
        INSERT OR REPLACE INTO members(
            user_id,
            chat_id,
            username,
            first_name
        )
        VALUES(?,?,?,?)
        """, (
            user_id,
            chat_id,
            username,
            first_name,
        ))

        await db.commit()


async def remove_member(
    chat_id: int,
    user_id: int,
):

    async with await get_db() as db:

        await db.execute("""
        DELETE FROM members
        WHERE chat_id=?
        AND user_id=?
        """, (
            chat_id,
            user_id,
        ))

        await db.commit()
