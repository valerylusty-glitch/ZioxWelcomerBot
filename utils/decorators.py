"""
utils/decorators.py

Décorateurs réutilisables.
"""

# ======================================================
# IMPORTS
# ======================================================

from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from utils.permissions import is_admin
from locales import t


# ======================================================
# ADMIN ONLY
# ======================================================

def admin_only(func):
    """
    Autorise uniquement les administrateurs.
    """

    @wraps(func)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        *args,
        **kwargs,
    ):

        if not await is_admin(update):

            await update.message.reply_text(
                t("NOT_ADMIN")
            )

            return

        return await func(
            update,
            context,
            *args,
            **kwargs,
        )

    return wrapper
