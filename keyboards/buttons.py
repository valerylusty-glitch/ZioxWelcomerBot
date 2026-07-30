"""
keyboards/buttons.py

Contient tous les claviers InlineKeyboard du bot.
"""

# ======================================================
# IMPORTS
# ======================================================

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


# ======================================================
# BOUTON RÈGLES
# ======================================================

def rules_keyboard() -> InlineKeyboardMarkup:
    """
    Bouton permettant d'afficher les règles.
    """

    keyboard = [
        [
            InlineKeyboardButton(
                text="📜 Voir les règles",
                callback_data="rules",
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


# ======================================================
# MENU PRINCIPAL
# ======================================================

def main_menu() -> InlineKeyboardMarkup:
    """
    Menu principal.
    """

    keyboard = [

        [
            InlineKeyboardButton(
                text="📜 Règles",
                callback_data="rules",
            ),

            InlineKeyboardButton(
                text="ℹ️ Aide",
                callback_data="help",
            ),
        ],

        [
            InlineKeyboardButton(
                text="➕ Ajouter le bot",
                url="https://t.me/ZioxWelcomerBot",
            )
        ],

    ]

    return InlineKeyboardMarkup(keyboard)
