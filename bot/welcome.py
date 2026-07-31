"""
Système d'accueil et d'au revoir personnalisable par groupe :
- Texte personnalisé (avec {prenom} et {groupe} comme variables)
- Message vocal/audio personnalisé
- Activation / désactivation indépendante des deux
"""

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from database import SessionLocal, ParametresGroupe
from moderation import est_admin


def get_parametres(session, chat_id: int) -> ParametresGroupe:
    params = session.get(ParametresGroupe, chat_id)
    if not params:
        params = ParametresGroupe(chat_id=chat_id)
        session.add(params)
        session.commit()
    return params


# ----------------------------------------------------------------------
# COMMANDES DE CONFIGURATION (admin uniquement)
# ----------------------------------------------------------------------

async def cmd_accueil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await est_admin(update, context):
        await update.message.reply_text("🚫 Réservé aux administrateurs.")
        return

    if not context.args:
        await update.message.reply_text(
            "ℹ️ <b>Configuration de l'accueil</b>\n\n"
            "/accueil on | off — activer / désactiver\n"
            "/accueil texte &lt;message&gt; — définir le texte (variables : {prenom} {groupe})\n"
            "/accueil audio — répondre à un vocal avec cette commande pour le définir\n"
            "/accueil test — prévisualiser le message actuel",
            parse_mode=ParseMode.HTML,
        )
        return

    sous_commande = context.args[0].lower()
    session = SessionLocal()
    try:
        params = get_parametres(session, update.effective_chat.id)

        if sous_commande == "on":
            params.accueil_actif = True
            session.commit()
            await update.message.reply_text("✅ Accueil activé.")

        elif sous_commande == "off":
            params.accueil_actif = False
            session.commit()
            await update.message.reply_text("🔕 Accueil désactivé.")

        elif sous_commande == "texte":
            nouveau_texte = update.message.text.split(maxsplit=2)
            if len(nouveau_texte) < 3:
                await update.message.reply_text("ℹ️ Utilisation : /accueil texte Bienvenue {prenom} !")
                return
            params.accueil_texte = nouveau_texte[2]
            session.commit()
            await update.message.reply_text("✅ Texte d'accueil mis à jour.")

        elif sous_commande == "audio":
            if not update.message.reply_to_message or not (
                update.message.reply_to_message.voice or update.message.reply_to_message.audio
            ):
                await update.message.reply_text("ℹ️ Réponds à un message vocal/audio avec /accueil audio.")
                return
            media = update.message.reply_to_message.voice or update.message.reply_to_message.audio
            params.accueil_audio_file_id = media.file_id
            session.commit()
            await update.message.reply_text("✅ Audio d'accueil enregistré.")

        elif sous_commande == "test":
            texte = params.accueil_texte.format(
                prenom=update.effective_user.first_name,
                groupe=update.effective_chat.title or "ce groupe",
            )
            await update.message.reply_text(texte, parse_mode=ParseMode.HTML)
            if params.accueil_audio_file_id:
                await update.message.reply_voice(params.accueil_audio_file_id)

        else:
            await update.message.reply_text("ℹ️ Sous-commande inconnue. Utilise /accueil sans argument pour l'aide.")
    finally:
        session.close()


async def cmd_aurevoir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await est_admin(update, context):
        await update.message.reply_text("🚫 Réservé aux administrateurs.")
        return

    if not context.args:
        await update.message.reply_text(
            "ℹ️ <b>Configuration de l'au revoir</b>\n\n"
            "/aurevoir on | off — activer / désactiver\n"
            "/aurevoir texte &lt;message&gt; — définir le texte (variables : {prenom} {groupe})\n"
            "/aurevoir audio — répondre à un vocal avec cette commande pour le définir\n"
            "/aurevoir test — prévisualiser le message actuel",
            parse_mode=ParseMode.HTML,
        )
        return

    sous_commande = context.args[0].lower()
    session = SessionLocal()
    try:
        params = get_parametres(session, update.effective_chat.id)

        if sous_commande == "on":
            params.aurevoir_actif = True
            session.commit()
            await update.message.reply_text("✅ Au revoir activé.")

        elif sous_commande == "off":
            params.aurevoir_actif = False
            session.commit()
            await update.message.reply_text("🔕 Au revoir désactivé.")

        elif sous_commande == "texte":
            nouveau_texte = update.message.text.split(maxsplit=2)
            if len(nouveau_texte) < 3:
                await update.message.reply_text("ℹ️ Utilisation : /aurevoir texte À bientôt {prenom} !")
                return
            params.aurevoir_texte = nouveau_texte[2]
            session.commit()
            await update.message.reply_text("✅ Texte d'au revoir mis à jour.")

        elif sous_commande == "audio":
            if not update.message.reply_to_message or not (
                update.message.reply_to_message.voice or update.message.reply_to_message.audio
            ):
                await update.message.reply_text("ℹ️ Réponds à un message vocal/audio avec /aurevoir audio.")
                return
            media = update.message.reply_to_message.voice or update.message.reply_to_message.audio
            params.aurevoir_audio_file_id = media.file_id
            session.commit()
            await update.message.reply_text("✅ Audio d'au revoir enregistré.")

        elif sous_commande == "test":
            texte = params.aurevoir_texte.format(
                prenom=update.effective_user.first_name,
                groupe=update.effective_chat.title or "ce groupe",
            )
            await update.message.reply_text(texte, parse_mode=ParseMode.HTML)
            if params.aurevoir_audio_file_id:
                await update.message.reply_voice(params.aurevoir_audio_file_id)

        else:
            await update.message.reply_text("ℹ️ Sous-commande inconnue. Utilise /aurevoir sans argument pour l'aide.")
    finally:
        session.close()


# ----------------------------------------------------------------------
# DÉCLENCHEURS AUTOMATIQUES
# ----------------------------------------------------------------------

async def sur_nouveau_membre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()
    try:
        params = get_parametres(session, update.effective_chat.id)
        if not params.accueil_actif:
            return
        for membre in update.message.new_chat_members:
            if membre.is_bot:
                continue
            texte = params.accueil_texte.format(
                prenom=membre.first_name,
                groupe=update.effective_chat.title or "ce groupe",
            )
            await update.message.reply_text(texte, parse_mode=ParseMode.HTML)
            if params.accueil_audio_file_id:
                await update.message.reply_voice(params.accueil_audio_file_id)
    finally:
        session.close()


async def sur_depart_membre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()
    try:
        params = get_parametres(session, update.effective_chat.id)
        if not params.aurevoir_actif:
            return
        membre = update.message.left_chat_member
        if not membre or membre.is_bot:
            return
        texte = params.aurevoir_texte.format(
            prenom=membre.first_name,
            groupe=update.effective_chat.title or "ce groupe",
        )
        await update.message.reply_text(texte, parse_mode=ParseMode.HTML)
        if params.aurevoir_audio_file_id:
            await update.message.reply_voice(params.aurevoir_audio_file_id)
    finally:
        session.close()
