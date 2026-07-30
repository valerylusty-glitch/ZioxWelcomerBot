"""
database/captcha.py

Gestion des captchas.
"""

from .connection import get_db


# ======================================================
# TABLE
# ======================================================

async def initialize_captcha():

    async with await get_db() as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS captcha(

            chat_id INTEGER,
            user_id INTEGER,

            message_id INTEGER,

            verified INTEGER DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            PRIMARY KEY(chat_id, user_id)

        )
        """)

        await db.commit()


# ======================================================
# CRUD
# ======================================================

async def create_captcha(
    chat_id: int,
    user_id: int,
    message_id: int,
):

    async with await get_db() as db:

        await db.execute("""
        INSERT OR REPLACE INTO captcha(
            chat_id,
            user_id,
            message_id
        )
        VALUES(?,?,?)
        """, (
            chat_id,
            user_id,
            message_id,
        ))

        await db.commit()


async def get_captcha(
    chat_id: int,
    user_id: int,
):

    async with await get_db() as db:

        cursor = await db.execute("""
        SELECT *
        FROM captcha
        WHERE chat_id=?
        AND user_id=?
        """, (
            chat_id,
            user_id,
        ))

        return await cursor.fetchone()


async def verify_captcha(
    chat_id: int,
    user_id: int,
):

    async with await get_db() as db:

        await db.execute("""
        UPDATE captcha
        SET verified=1
        WHERE chat_id=?
        AND user_id=?
        """, (
            chat_id,
            user_id,
        ))

        await db.commit()


async def delete_captcha(
    chat_id: int,
    user_id: int,
):

    async with await get_db() as db:

        await db.execute("""
        DELETE FROM captcha
        WHERE chat_id=?
        AND user_id=?
        """, (
            chat_id,
            user_id,
        ))

        await db.commit()
