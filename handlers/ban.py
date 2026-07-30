"""
handlers/ban.py
Commandes de bannissement.
"""
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from utils.decorators import admin_only

@admin_only
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ <b>Répondez</b> au message de l'utilisateur à bannir.", parse_mode="HTML")
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"🚫 <b>{user.full_name}</b> a été banni.", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Erreur : {e}")

def register_ban(app: Application):
    app.add_handler(CommandHandler("ban", ban_command))
