"""
handlers/unban.py
Commandes de débannissement.
"""
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from utils.decorators import admin_only

@admin_only
async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Utilisation : <code>/unban &lt;user_id&gt;</code>", parse_mode="HTML")
    try:
        user_id = int(context.args[0])
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text(f"✅ Utilisateur <code>{user_id}</code> débanni.", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Erreur : {e}")

def register_unban(app: Application):
    app.add_handler(CommandHandler("unban", unban_command))
