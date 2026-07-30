"""
handlers/welcome.py
Gestion des nouveaux membres avec téléchargement de l'avatar.
"""
import os
from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)
from database import database
from utils.image import create_welcome_card

async def welcome_member(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Déclenché lorsqu'un ou plusieurs membres rejoignent le groupe.
    """
    if update.message is None:
        return

    chat = update.effective_chat
    
    # Crée le groupe s'il n'existe pas
    await database.create_group(chat.id, chat.title)
    group = await database.get_group(chat.id)

    for member in update.message.new_chat_members:
        # Sauvegarde du membre
        await database.add_member(
            chat_id=chat.id,
            user_id=member.id,
            username=member.username,
            first_name=member.first_name,
        )

        # Sauvegarde dans les logs
        await database.log(chat.id, member.id, "JOIN")

        # Télécharger la photo de profil
        avatar_path = f"assets/avatars_{member.id}.png"
        os.makedirs("assets", exist_ok=True)
        
        try:
            photos = await context.bot.get_user_profile_photos(member.id, limit=1)
            if photos.total_count > 0:
                file = await context.bot.get_file(photos.photos[0][-1].file_id)
                await file.download_to_drive(avatar_path)
            else:
                avatar_path = None
        except Exception as e:
            print(f"Erreur téléchargement photo: {e}")
            avatar_path = None

        # Générer la carte
        card = create_welcome_card(
            member.full_name,
            chat.title,
            avatar_path
        )

        # Message de bienvenue
        welcome_text = group["welcome_message"]
        welcome_text = (
            welcome_text
            .replace("{user}", member.mention_html())
            .replace("{group}", chat.title)
        )

        await update.message.reply_photo(
            photo=card,
            caption=welcome_text,
            parse_mode="HTML",
        )
        
        # Nettoyage
        if avatar_path and os.path.exists(avatar_path):
            os.remove(avatar_path)

def register_welcome(app: Application):
    """
    Enregistre le handler de bienvenue.
    """
    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            welcome_member,
        )
    )
