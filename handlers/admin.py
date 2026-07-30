"""
handlers/admin.py

Commandes administrateur.
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
    set_welcome,
    set_goodbye,
    set_rules,
)


# ======================================================
# OUTILS
# ======================================================

async def is_admin(update: Update) -> bool:
    """
    Vérifie si l'utilisateur est administrateur du groupe.
    """

    member = await update.effective_chat.get_member(
        update.effective_user.id
    )

    return member.status in (
        "administrator",
        "creator",
    )


# ======================================================
# /setwelcome
# ======================================================

async def setwelcome_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Modifie le message de bienvenue.
    """

    if not await is_admin(update):
        await update.message.reply_text(
            "❌ Tu dois être administrateur."
        )
        return

    if not context.args:

        await update.message.reply_text(
            "Utilisation :\n"
            "/setwelcome Bonjour {user}"
        )

        return

    message = " ".join(context.args)

    await set_welcome(
        update.effective_chat.id,
        message,
    )

    await update.message.reply_text(
        "✅ Message de bienvenue enregistré."
    )


# ======================================================
# /setgoodbye
# ======================================================

async def setgoodbye_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not await is_admin(update):

        await update.message.reply_text(
            "❌ Tu dois être administrateur."
        )

        return

    if not context.args:

        await update.message.reply_text(
            "Utilisation :\n"
            "/setgoodbye Au revoir {user}"
        )

        return

    message = " ".join(context.args)

    await set_goodbye(
        update.effective_chat.id,
        message,
    )

    await update.message.reply_text(
        "✅ Message d'au revoir enregistré."
    )


# ======================================================
# /setrules
# ======================================================

async def setrules_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not await is_admin(update):

        await update.message.reply_text(
            "❌ Tu dois être administrateur."
        )

        return

    if not context.args:

        await update.message.reply_text(
            "Utilisation :\n"
            "/setrules ..."
        )

        return

    rules = " ".join(context.args)

    await set_rules(
        update.effective_chat.id,
        rules,
    )

    await update.message.reply_text(
        "✅ Règles enregistrées."
    )


# ======================================================
# REGISTER
# ======================================================

def register_admin(app: Application):

    app.add_handler(
        CommandHandler(
            "setwelcome",
            setwelcome_command,
        )
    )

    app.add_handler(
        CommandHandler(
            "setgoodbye",
            setgoodbye_command,
        )
    )

    app.add_handler(
        CommandHandler(
            "setrules",
            setrules_command,
        )
    )
