"""
Système de modération : kick, ban, unban, mute, unmute, warn, unwarn, warns.
Toutes les commandes vérifient que l'exécutant est administrateur du groupe.
"""

from datetime import datetime, timedelta

from telegram import Update, ChatPermissions
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from database import SessionLocal, Avertissement

SEUIL_WARN_AVANT_BAN = 3


# ----------------------------------------------------------------------
# OUTILS
# ----------------------------------------------------------------------

async def est_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    membre = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    return membre.status in ("administrator", "creator")


async def extraire_cible(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Récupère l'utilisateur ciblé : soit par réponse à un message, soit par @mention."""
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    if context.args:
        pseudo = context.args[0].lstrip("@")
        # Telegram ne permet pas de résoudre un @pseudo en ID sans que l'utilisateur ait interagi.
        # On invite donc à utiliser la réponse à un message pour plus de fiabilité.
        return None
    return None


def raison_depuis_args(context, decalage=0):
    if len(context.args) > decalage:
        return " ".join(context.args[decalage:])
    return "Non précisée"


# ----------------------------------------------------------------------
# COMMANDES
# ----------------------------------------------------------------------

async def cmd_kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await est_admin(update, context):
        await update.message.reply_text("🚫 Réservé aux administrateurs.")
        return
    cible = await extraire_cible(update, context)
    if not cible:
        await update.message.reply_text("ℹ️ Réponds au message de la personne avec /kick pour l'expulser.")
        return

    chat_id = update.effective_chat.id
    await context.bot.ban_chat_member(chat_id, cible.id)
    await context.bot.unban_chat_member(chat_id, cible.id)  # unban immédiat = simple expulsion, pas un ban définitif
    raison = raison_depuis_args(context)
    await update.message.reply_text(
        f"👢 <b>{cible.first_name}</b> a été expulsé du groupe.\nRaison : {raison}",
        parse_mode=ParseMode.HTML,
    )


async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await est_admin(update, context):
        await update.message.reply_text("🚫 Réservé aux administrateurs.")
        return
    cible = await extraire_cible(update, context)
    if not cible:
        await update.message.reply_text("ℹ️ Réponds au message de la personne avec /ban pour la bannir.")
        return

    await context.bot.ban_chat_member(update.effective_chat.id, cible.id)
    raison = raison_depuis_args(context)
    await update.message.reply_text(
        f"⛔ <b>{cible.first_name}</b> a été banni du groupe.\nRaison : {raison}",
        parse_mode=ParseMode.HTML,
    )


async def cmd_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await est_admin(update, context):
        await update.message.reply_text("🚫 Réservé aux administrateurs.")
        return
    if not context.args or not context.args[0].lstrip("-").isdigit():
        await update.message.reply_text("ℹ️ Utilisation : /unban <id_telegram>")
        return

    user_id = int(context.args[0])
    await context.bot.unban_chat_member(update.effective_chat.id, user_id)
    await update.message.reply_text(f"✅ L'utilisateur <code>{user_id}</code> a été débanni.", parse_mode=ParseMode.HTML)


async def cmd_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await est_admin(update, context):
        await update.message.reply_text("🚫 Réservé aux administrateurs.")
        return
    cible = await extraire_cible(update, context)
    if not cible:
        await update.message.reply_text("ℹ️ Réponds au message de la personne avec /mute [minutes] pour la museler.")
        return

    minutes = None
    if context.args and context.args[0].isdigit():
        minutes = int(context.args[0])

    until = datetime.utcnow() + timedelta(minutes=minutes) if minutes else None
    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        cible.id,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=until,
    )
    duree = f"pendant {minutes} min" if minutes else "indéfiniment"
    await update.message.reply_text(
        f"🔇 <b>{cible.first_name}</b> a été muté {duree}.", parse_mode=ParseMode.HTML
    )


async def cmd_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await est_admin(update, context):
        await update.message.reply_text("🚫 Réservé aux administrateurs.")
        return
    cible = await extraire_cible(update, context)
    if not cible:
        await update.message.reply_text("ℹ️ Réponds au message de la personne avec /unmute pour la démuseler.")
        return

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        cible.id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        ),
    )
    await update.message.reply_text(f"🔊 <b>{cible.first_name}</b> peut de nouveau écrire.", parse_mode=ParseMode.HTML)


async def cmd_warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await est_admin(update, context):
        await update.message.reply_text("🚫 Réservé aux administrateurs.")
        return
    cible = await extraire_cible(update, context)
    if not cible:
        await update.message.reply_text("ℹ️ Réponds au message de la personne avec /warn <raison>.")
        return

    raison = raison_depuis_args(context)
    session = SessionLocal()
    try:
        session.add(Avertissement(chat_id=update.effective_chat.id, user_id=cible.id, raison=raison))
        session.commit()
        total = session.query(Avertissement).filter_by(
            chat_id=update.effective_chat.id, user_id=cible.id
        ).count()
    finally:
        session.close()

    await update.message.reply_text(
        f"⚠️ <b>{cible.first_name}</b> a reçu un avertissement ({total}/{SEUIL_WARN_AVANT_BAN}).\nRaison : {raison}",
        parse_mode=ParseMode.HTML,
    )

    if total >= SEUIL_WARN_AVANT_BAN:
        await context.bot.ban_chat_member(update.effective_chat.id, cible.id)
        await update.message.reply_text(
            f"⛔ <b>{cible.first_name}</b> a atteint {SEUIL_WARN_AVANT_BAN} avertissements et a été banni automatiquement.",
            parse_mode=ParseMode.HTML,
        )


async def cmd_unwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await est_admin(update, context):
        await update.message.reply_text("🚫 Réservé aux administrateurs.")
        return
    cible = await extraire_cible(update, context)
    if not cible:
        await update.message.reply_text("ℹ️ Réponds au message de la personne avec /unwarn.")
        return

    session = SessionLocal()
    try:
        dernier = (
            session.query(Avertissement)
            .filter_by(chat_id=update.effective_chat.id, user_id=cible.id)
            .order_by(Avertissement.id.desc())
            .first()
        )
        if dernier:
            session.delete(dernier)
            session.commit()
            total = session.query(Avertissement).filter_by(
                chat_id=update.effective_chat.id, user_id=cible.id
            ).count()
            await update.message.reply_text(
                f"✅ Un avertissement retiré à <b>{cible.first_name}</b> ({total}/{SEUIL_WARN_AVANT_BAN}).",
                parse_mode=ParseMode.HTML,
            )
        else:
            await update.message.reply_text(f"{cible.first_name} n'a aucun avertissement.")
    finally:
        session.close()


async def cmd_warns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cible = await extraire_cible(update, context) or update.effective_user
    session = SessionLocal()
    try:
        total = session.query(Avertissement).filter_by(
            chat_id=update.effective_chat.id, user_id=cible.id
        ).count()
    finally:
        session.close()
    await update.message.reply_text(
        f"⚠️ <b>{cible.first_name}</b> a {total}/{SEUIL_WARN_AVANT_BAN} avertissement(s).",
        parse_mode=ParseMode.HTML,
    )
