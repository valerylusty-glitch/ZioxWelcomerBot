"""
handlers/callbacks.py

Gestion des boutons InlineKeyboard.
"""

# ======================================================
# IMPORTS
# ======================================================

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ContextTypes,
)

from database import get_group


# ======================================================
# CALLBACKS
# ======================================================

async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Gestion des boutons.
    """

    query = update.callback_query

    await query.answer()

    data = query.data

    chat = query.message.chat

    # ==========================================
    # RÈGLES
    # ==========================================

    if data == "rules":

        group = await get_group(chat.id)

        rules = group["rules"]

        if not rules:
            rules = "📜 Aucune règle n'a encore été définie."

        await query.edit_message_text(rules)

        return

    # ==========================================
    # AIDE
    # ==========================================

    if data == "help":

        await query.edit_message_text(
            "📚 ZioxWelcomer\n\n"
            "/start\n"
            "/help\n"
            "/rules"
        )

        return

# ======================================================
# REGISTER
# ======================================================

def register_callbacks(app: Application):
    """
    Enregistre les callbacks.
    """

    app.add_handler(
        CallbackQueryHandler(
            callback_handler
        )
    )
