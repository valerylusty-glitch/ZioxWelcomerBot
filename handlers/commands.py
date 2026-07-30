"""
handlers/commands.py
Gestion des commandes publiques et de gestion de groupe.
"""
from telegram import Update, constants
from telegram.ext import Application, CommandHandler, ContextTypes
from database import database
from keyboards.buttons import start_menu_keyboard
from utils.decorators import admin_only

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /start avec menu stylisé."""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type != constants.ChatType.PRIVATE:
        await database.create_group(chat.id, chat.title)
        return await update.message.reply_text("👋 Bot actif dans ce groupe !")

    text = (
        f"👋 <b>Bienvenue {user.first_name} !</b>\n\n"
        "Je suis <b>ZioxWelcomer</b>, un bot de gestion de groupe avancé.\n\n"
        "✨ <b>Mes capacités :</b>\n"
        "• Cartes de bienvenue avec photos\n"
        "• Système de modération complet\n"
        "• Gestion des règles et logs\n"
        "• Captcha anti-bot\n\n"
        "<i>Utilisez les boutons ci-dessous pour explorer mes fonctions.</i>"
    )
    await update.message.reply_text(
        text=text,
        reply_markup=start_menu_keyboard(),
        parse_mode="HTML"
    )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche les informations d'un utilisateur."""
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    
    try:
        chat_member = await context.bot.get_chat(target.id)
        bio = getattr(chat_member, 'bio', 'Aucune bio')
    except:
        bio = "Non disponible"

    text = (
        f"👤 <b>INFORMATIONS UTILISATEUR</b>\n\n"
        f"▫️ <b>Nom :</b> {target.full_name}\n"
        f"▫️ <b>ID :</b> <code>{target.id}</code>\n"
        f"▫️ <b>Pseudo :</b> @{target.username if target.username else 'Aucun'}\n"
        f"▫️ <b>Bio :</b> <i>{bio}</i>\n"
        f"▫️ <b>Lien :</b> <a href='tg://user?id={target.id}'>Lien permanent</a>"
    )
    await update.message.reply_text(text, parse_mode="HTML")

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche les IDs."""
    text = (
        f"🆔 <b>DÉTAILS DES IDENTIFIANTS</b>\n\n"
        f"👤 <b>Votre ID :</b> <code>{update.effective_user.id}</code>\n"
        f"👥 <b>Chat ID :</b> <code>{update.effective_chat.id}</code>"
    )
    await update.message.reply_text(text, parse_mode="HTML")

@admin_only
async def pin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Épingler un message."""
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Répondez au message à épingler.")
    await update.message.reply_to_message.pin()
    await update.message.reply_text("📌 Message épinglé avec succès.")

@admin_only
async def unpin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Désépingler un message."""
    await context.bot.unpin_chat_message(update.effective_chat.id)
    await update.message.reply_text("📍 Dernier message épinglé retiré.")

async def staff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Liste les administrateurs du groupe."""
    admins = await context.bot.get_chat_administrators(update.effective_chat.id)
    text = "👮 <b>STAFF DU GROUPE</b>\n\n"
    for admin in admins:
        status = "👑 Créateur" if admin.status == constants.ChatMemberStatus.OWNER else "🛡 Admin"
        text += f"• {admin.user.full_name} [{status}]\n"
    await update.message.reply_text(text, parse_mode="HTML")

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche les règles du groupe."""
    chat = update.effective_chat
    group = await database.get_group(chat.id)
    if not group or not group.get("rules"):
        return await update.message.reply_text("📜 Aucune règle n'a été définie pour ce groupe.")
    
    text = f"📜 <b>RÈGLES DE {chat.title}</b>\n\n{group['rules']}"
    await update.message.reply_text(text, parse_mode="HTML")

def register_commands(app: Application):
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("pin", pin_command))
    app.add_handler(CommandHandler("unpin", unpin_command))
    app.add_handler(CommandHandler("staff", staff_command))
    app.add_handler(CommandHandler("rules", rules_command))
