"""
handlers/member.py

Gestion des membres.
"""

from telegram import Update, ChatPermissions
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from utils import admin_only

# ======================================================
# REGISTER
# ======================================================

def register_member(app: Application):
    """
    Enregistre les commandes de gestion des membres.
    """

    app.add_handler(CommandHandler("kick", kick_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("unban", unban_command))
    app.add_handler(CommandHandler("mute", mute_command))
    app.add_handler(CommandHandler("unmute", unmute_command))
