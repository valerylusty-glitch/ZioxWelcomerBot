"""
handlers/mute.py
Commandes de sourdine.
"""
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, ContextTypes
from utils.decorators import admin_only

@admin_only
async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ <b>Répondez</b> au message de l'utilisateur.", parse_mode="HTML")
    user = update.message.reply_to_message.from_user
    permissions = ChatPermissions(can_send_messages=False)
    try:
        await context.bot.restrict_chat_member(update.effective_chat.id, user.id, permissions=permissions)
        await update.message.reply_text(f"🔇 <b>{user.full_name}</b> a été réduit au silence.", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Erreur : {e}")

def register_mute(app: Application):
    app.add_handler(CommandHandler("mute", mute_command))
