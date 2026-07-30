"""
handlers/admin.py
Commandes administrateur avec style.
"""
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from database import set_welcome, set_goodbye, set_rules
from utils.decorators import admin_only

@admin_only
async def setwelcome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text(
            "📝 <b>Utilisation :</b>\n<code>/setwelcome Bonjour {user} !</code>\n\n"
            "<i>Variables : {user}, {group}</i>",
            parse_mode="HTML"
        )
    message = " ".join(context.args)
    await set_welcome(update.effective_chat.id, message)
    await update.message.reply_text("✅ <b>Message de bienvenue enregistré !</b>", parse_mode="HTML")

@admin_only
async def setgoodbye_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text(
            "📝 <b>Utilisation :</b>\n<code>/setgoodbye Au revoir {user} !</code>",
            parse_mode="HTML"
        )
    message = " ".join(context.args)
    await set_goodbye(update.effective_chat.id, message)
    await update.message.reply_text("✅ <b>Message d'au revoir enregistré !</b>", parse_mode="HTML")

@admin_only
async def setrules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text(
            "📝 <b>Utilisation :</b>\n<code>/setrules 1. Pas de spam...</code>",
            parse_mode="HTML"
        )
    rules = " ".join(context.args)
    await set_rules(update.effective_chat.id, rules)
    await update.message.reply_text("✅ <b>Règles du groupe enregistrées !</b>", parse_mode="HTML")

def register_admin(app: Application):
    app.add_handler(CommandHandler("setwelcome", setwelcome_command))
    app.add_handler(CommandHandler("setgoodbye", setgoodbye_command))
    app.add_handler(CommandHandler("setrules", setrules_command))
