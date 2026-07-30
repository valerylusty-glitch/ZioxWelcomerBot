"""
keyboards/buttons.py
Contient tous les claviers InlineKeyboard du bot.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def start_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Menu principal affiché lors du /start.
    """
    keyboard = [
        [
            InlineKeyboardButton("🛠 Commandes", callback_data="help"),
            InlineKeyboardButton("📜 Règles", callback_data="rules")
        ],
        [
            InlineKeyboardButton("📢 Canal", url="https://t.me/ZioxDev"),
            InlineKeyboardButton("👨‍💻 Support", url="https://t.me/valerylusty")
        ],
        [
            InlineKeyboardButton("➕ Ajouter à un groupe", url="https://t.me/ZioxWelcomerBot?startgroup=true")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def help_keyboard() -> InlineKeyboardMarkup:
    """
    Menu d'aide.
    """
    keyboard = [
        [
            InlineKeyboardButton("🛡 Modération", callback_data="help_mod"),
            InlineKeyboardButton("⚙️ Gestion", callback_data="help_admin")
        ],
        [
            InlineKeyboardButton("🔙 Retour", callback_data="start_back")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def rules_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton("📜 Voir les règles", callback_data="rules")]]
    return InlineKeyboardMarkup(keyboard)
