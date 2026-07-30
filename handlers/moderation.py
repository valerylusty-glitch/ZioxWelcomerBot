"""
handlers/moderation.py

Commandes de modération.
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
    add_warning,
    count_warnings,
    clear_warnings,
)

from utils import admin_only


# ======================================================
# /warn
# ======================================================

@admin_only
async def warn_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.message.reply_to_message:

        await update.message.reply_text(
            "⚠️ Réponds au message de l'utilisateur à avertir."
        )

        return

    member = update.message.reply_to_message.from_user

    reason = (
        " ".join(context.args)
        if context.args
        else "Aucune raison"
    )

    await add_warning(
        chat_id=update.effective_chat.id,
        user_id=member.id,
        admin_id=update.effective_user.id,
        reason=reason,
    )

    warns = await count_warnings(
        update.effective_chat.id,
        member.id,
    )

    await update.message.reply_text(
        f"⚠️ {member.full_name} possède maintenant {warns}/3 avertissements."
    )

    # Bannissement automatique
    if warns >= 3:

        try:

            await context.bot.ban_chat_member(
                update.effective_chat.id,
                member.id,
            )

            await update.message.reply_text(
                f"🚫 {member.full_name} a été banni (3 avertissements)."
            )

        except Exception as e:

            await update.message.reply_text(
                f"Erreur : {e}"
            )

      # ======================================================
# /warnings
# ======================================================

@admin_only
async def warnings_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.message.reply_to_message:

        await update.message.reply_text(
            "Réponds au message de l'utilisateur."
        )

        return

    member = update.message.reply_to_message.from_user

    warns = await count_warnings(
        update.effective_chat.id,
        member.id,
    )

    await update.message.reply_text(
        f"📋 {member.full_name} possède {warns} avertissement(s)."
    )

# ======================================================
# /clearwarnings
# ======================================================

@admin_only
async def clearwarnings_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.message.reply_to_message:

        await update.message.reply_text(
            "Réponds au message de l'utilisateur."
        )

        return

    member = update.message.reply_to_message.from_user

    await clear_warnings(
        update.effective_chat.id,
        member.id,
    )

    await update.message.reply_text(
        f"✅ Les avertissements de {member.full_name} ont été supprimés."
    )

# ======================================================
# REGISTER
# ======================================================

def register_moderation(app: Application):

    app.add_handler(
        CommandHandler(
            "warn",
            warn_command,
        )
    )

    app.add_handler(
        CommandHandler(
            "warnings",
            warnings_command,
        )
    )

    app.add_handler(
        CommandHandler(
            "clearwarnings",
            clearwarnings_command,
        )
    )
