"""
handlers/commands.py

Gestion des commandes publiques.
"""

# ======================================================
# IMPORTS
# ======================================================

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from database import (
    create_group,
    get_group,
)

from locales import t


# ======================================================
# COMMANDES
# ======================================================

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Commande /start
    """

    chat = update.effective_chat

    if chat:

        await create_group(
            chat.id,
            chat.title or "Conversation privée",
        )

    await update.message.reply_text(
        text=t("START"),
        parse_mode="Markdown",
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Commande /help
    """

    await update.message.reply_text(
        text=t("HELP"),
        parse_mode="Markdown",
    )


async def rules_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Commande /rules
    """

    chat = update.effective_chat

    group = await get_group(chat.id)

    if group is None:

        await update.message.reply_text(
            t("NO_RULES")
        )

        return

    rules = group["rules"]

    if not rules:

        await update.message.reply_text(
            t("NO_RULES")
        )

        return

    await update.message.reply_text(rules)


# ======================================================
# ENREGISTREMENT
# ======================================================

def register_commands(app: Application):
    """
    Enregistre les commandes.
    """

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("rules", rules_command))
