"""
handlers/unmute.py
Commandes de désactivation du silence.
"""
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, ContextTypes
from utils.decorators import admin_only

@admin_only
async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ <b>Répondez</b> au message de l'utilisateur.", parse_mode="HTML")
    user = update.message.reply_to_message.from_user
    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_invite_users=True
    )
    try:
        await context.bot.restrict_chat_member(update.effective_chat.id, user.id, permissions=permissions)
        await update.message.reply_text(f"🔊 <b>{user.full_name}</b> peut à nouveau parler.", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Erreur : {e}")

def register_unmute(app: Application):
    app.add_handler(CommandHandler("unmute", unmute_command))
