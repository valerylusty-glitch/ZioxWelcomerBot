"""
handlers/callbacks.py
Gestion des boutons InlineKeyboard avec style.
"""
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes
from database import database
from keyboards.buttons import start_menu_keyboard, help_keyboard

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "start_back":
        text = (
            f"👋 <b>Bienvenue !</b>\n\n"
            "Je suis <b>ZioxWelcomer</b>, un bot de gestion de groupe avancé.\n\n"
            "<i>Utilisez les boutons ci-dessous pour explorer mes fonctions.</i>"
        )
        await query.edit_message_text(text, reply_markup=start_menu_keyboard(), parse_mode="HTML")

    elif data == "help":
        text = (
            "📚 <b>MENU D'AIDE</b>\n\n"
            "Choisissez une catégorie pour voir les commandes disponibles :"
        )
        await query.edit_message_text(text, reply_markup=help_keyboard(), parse_mode="HTML")

    elif data == "help_mod":
        text = (
            "🛡 <b>COMMANDES DE MODÉRATION</b>\n\n"
            "• /warn - Avertir un membre (réponse)\n"
            "• /ban - Bannir un membre (réponse)\n"
            "• /kick - Expulser un membre (réponse)\n"
            "• /mute - Rendre muet (réponse)\n"
            "• /unmute - Redonner la parole (réponse)\n"
            "• /clearwarnings - Effacer les warns (réponse)"
        )
        await query.edit_message_text(text, reply_markup=help_keyboard(), parse_mode="HTML")

    elif data == "help_admin":
        text = (
            "⚙️ <b>COMMANDES DE GESTION</b>\n\n"
            "• /setwelcome - Configurer le message d'accueil\n"
            "• /setgoodbye - Configurer le message d'adieu\n"
            "• /setrules - Définir les règles du groupe\n"
            "• /pin - Épingler un message (réponse)\n"
            "• /unpin - Désépingler le message actuel\n"
            "• /staff - Voir la liste des administrateurs\n"
            "• /info - Voir les infos d'un membre\n"
            "• /id - Voir les IDs (utilisateur/groupe)"
        )
        await query.edit_message_text(text, reply_markup=help_keyboard(), parse_mode="HTML")

    elif data == "rules":
        group = await database.get_group(query.message.chat.id)
        rules = group.get("rules") if group else None
        if not rules:
            rules = "📜 Aucune règle n'a encore été définie."
        
        text = f"📜 <b>RÈGLES DU GROUPE</b>\n\n{rules}"
        await query.edit_message_text(text, reply_markup=help_keyboard(), parse_mode="HTML")

def register_callbacks(app: Application):
    app.add_handler(CallbackQueryHandler(callback_handler))
