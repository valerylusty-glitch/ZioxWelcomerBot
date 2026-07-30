"""
handlers/moderation.py
Commandes de modération avec style.
"""
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from database import add_warning, count_warnings, clear_warnings
from utils.decorators import admin_only

@admin_only
async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ <b>Répondez</b> au message de l'utilisateur à avertir.", parse_mode="HTML")
    
    member = update.message.reply_to_message.from_user
    reason = " ".join(context.args) if context.args else "Aucune raison spécifiée"
    
    await add_warning(
        chat_id=update.effective_chat.id,
        user_id=member.id,
        admin_id=update.effective_user.id,
        reason=reason,
    )
    
    warns = await count_warnings(update.effective_chat.id, member.id)
    text = (
        f"⚠️ <b>AVERTISSEMENT</b>\n\n"
        f"👤 <b>Utilisateur :</b> {member.full_name}\n"
        f"🔢 <b>Warns :</b> {warns}/3\n"
        f"📝 <b>Raison :</b> <i>{reason}</i>"
    )
    await update.message.reply_text(text, parse_mode="HTML")
    
    if warns >= 3:
        try:
            await context.bot.ban_chat_member(update.effective_chat.id, member.id)
            await update.message.reply_text(f"🚫 <b>{member.full_name}</b> a été banni pour avoir atteint 3 avertissements.", parse_mode="HTML")
        except Exception as e:
            await update.message.reply_text(f"❌ Erreur lors du bannissement : {e}")

@admin_only
async def warnings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    warns = await count_warnings(update.effective_chat.id, target.id)
    await update.message.reply_text(f"📋 <b>{target.full_name}</b> possède <code>{warns}</code> avertissement(s).", parse_mode="HTML")

@admin_only
async def clearwarnings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Répondez au message de l'utilisateur.", parse_mode="HTML")
    
    member = update.message.reply_to_message.from_user
    await clear_warnings(update.effective_chat.id, member.id)
    await update.message.reply_text(f"✅ Les avertissements de <b>{member.full_name}</b> ont été réinitialisés.", parse_mode="HTML")

def register_moderation(app: Application):
    app.add_handler(CommandHandler("warn", warn_command))
    app.add_handler(CommandHandler("warnings", warnings_command))
    app.add_handler(CommandHandler("clearwarnings", clearwarnings_command))
