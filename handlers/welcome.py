"""
handlers/welcome.py

Gestion des nouveaux membres.
"""

# ======================================================
# IMPORTS
# ======================================================

from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)

from database import database
from utils.image import create_welcome_card

# ======================================================
# NOUVEAUX MEMBRES
# ======================================================

async def welcome_member(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Déclenché lorsqu'un ou plusieurs membres rejoignent le groupe.
    """

    if update.message is None:
        return

    chat = update.effective_chat

    # Crée le groupe s'il n'existe pas
    await database.create_group(
        chat.id,
        chat.title,
    )

    group = await database.get_group(chat.id)

    for member in update.message.new_chat_members:

        # Sauvegarde du membre
        await database.add_member(
            chat_id=chat.id,
            user_id=member.id,
            username=member.username,
            first_name=member.first_name,
        )

        # Sauvegarde dans les logs
        await database.log(
            chat.id,
            member.id,
            "JOIN",
        )

        # Message de bienvenue
        welcome = group["welcome_message"]

        welcome = (
            welcome
            .replace("{user}", member.mention_html())
            .replace("{group}", chat.title)
        )

        card = create_welcome_card(
    member.full_name,
    chat.title,
)

await update.message.reply_photo(
    photo=card,
    caption=welcome,
    parse_mode="HTML",
)

# ======================================================
# ENREGISTREMENT
# ======================================================

def register_welcome(app: Application):
    """
    Enregistre le handler de bienvenue.
    """

    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            welcome_member,
        )
    )
