"""
utils/helpers.py

Fonctions utilitaires diverses.
"""

from telegram import Update


def get_chat_id(update: Update) -> int | None:
    """
    Retourne l'identifiant du chat.
    """

    if update.effective_chat:
        return update.effective_chat.id

    return None


def get_user_id(update: Update) -> int | None:
    """
    Retourne l'identifiant de l'utilisateur.
    """

    if update.effective_user:
        return update.effective_user.id

    return None
