"""
Point d'entrée du bot Ziox.
Assemble : accueil/au revoir, modération, famille, groupes, et le lien vers la mini-app.
"""

import os
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters,
)

from database import init_db, SessionLocal, get_or_create_user, CompteBancaire
import moderation
import welcome
import family
import games
import groups

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "PLACE_TON_TOKEN_ICI")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://ton-domaine.exemple/webapp/index.html")


def clavier_principal() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏙️ Ouvrir Ziox", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("💳 Mon solde", callback_data="solde")],
    ])


async def cmd_start(update: Update, context):
    await update.message.reply_text(
        f"✨ <b>Bienvenue {update.effective_user.first_name} !</b> ✨\n\n"
        "Je suis <b>Ziox Bot</b> : accueil personnalisé, modération, "
        "système familial et la mini-ville <b>Ziox</b>.\n\n"
        "Tape /help pour la liste complète des commandes.",
        parse_mode=ParseMode.HTML,
        reply_markup=clavier_principal(),
    )


async def cmd_help(update: Update, context):
    help_text = (
        "🛠️ <b>Commandes disponibles</b>\n\n"
        "<b>🏠 Général</b>\n"
        "/start — Menu principal\n"
        "/profil — Voir mon profil Ziox\n"
        "/solde — Voir mon solde bancaire\n\n"
        "<b>👨‍👩‍👧 Famille</b>\n"
        "/famille — Créer, inviter, accepter, quitter\n\n"
        "<b>🎮 Jeux (avec de vraies ZCoins)</b>\n"
        "/machine &lt;mise&gt; — 🎰 Machine à sous (solo)\n"
        "/duel &lt;mise&gt; — ⚔️ Défier un joueur (répondre à son message)\n\n"
        "<b>⚙️ Configuration Accueil (admins)</b>\n"
        "/accueil — Configurer le message de bienvenue\n"
        "/aurevoir — Configurer le message de départ\n\n"
        "<b>👮 Modération (admins)</b>\n"
        "/kick /ban /unban /mute /unmute /warn /unwarn /warns\n"
        "(répondre au message de la personne concernée)\n\n"
        "<b>👥 Gestion Groupe (admins)</b>\n"
        "/tagall &lt;message&gt; — Mentionner tous les actifs\n"
        "/leaderboard — Classement des chatteurs\n"
        "/leaderboard_groups — Classement des groupes\n"
        "/stats — Statistiques du groupe\n"
        "/mystats — Tes statistiques personnelles\n"
        "/reset_stats confirm — Réinitialiser les stats"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)


async def cmd_profil(update: Update, context):
    session = SessionLocal()
    try:
        user = get_or_create_user(session, update.effective_user)
        compte = session.get(CompteBancaire, user.id)
        texte = (
            f"👤 <b>Profil de {update.effective_user.first_name}</b>\n\n"
            f"🌍 Nationalité : {user.nationalite or 'non renseignée'}\n"
            f"🎂 Âge : {user.age or 'non renseigné'}\n"
            f"⚧ Sexe : {user.sexe or 'non renseigné'}\n"
            f"🎓 Diplôme : {user.diplome or 'non renseigné'}\n"
            f"💞 Statut : {user.statut_relationnel}\n"
            f"💰 Solde : {compte.solde:.2f} ZCoins\n\n"
            "Complète ou modifie ton profil dans la mini-app 👇"
        )
        await update.message.reply_text(
            texte, parse_mode=ParseMode.HTML, reply_markup=clavier_principal()
        )
    finally:
        session.close()


async def cmd_solde(update: Update, context):
    session = SessionLocal()
    try:
        user = get_or_create_user(session, update.effective_user)
        compte = session.get(CompteBancaire, user.id)
        await update.message.reply_text(
            f"💳 Compte <code>{compte.numero_compte}</code>\n💰 Solde : <b>{compte.solde:.2f} ZCoins</b>",
            parse_mode=ParseMode.HTML,
        )
    finally:
        session.close()


def main():
    init_db()
    app: Application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Général
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("profil", cmd_profil))
    app.add_handler(CommandHandler("solde", cmd_solde))

    # Famille
    app.add_handler(CommandHandler("famille", family.cmd_famille))

    # Jeux
    app.add_handler(CommandHandler("machine", games.cmd_machine))
    app.add_handler(CommandHandler("duel", games.cmd_duel))
    app.add_handler(CallbackQueryHandler(games.gerer_callback_duel, pattern="^duel_"))

    # Accueil / au revoir
    app.add_handler(CommandHandler("accueil", welcome.cmd_accueil))
    app.add_handler(CommandHandler("aurevoir", welcome.cmd_aurevoir))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome.sur_nouveau_membre))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, welcome.sur_depart_membre))

    # Modération
    app.add_handler(CommandHandler("kick", moderation.cmd_kick))
    app.add_handler(CommandHandler("ban", moderation.cmd_ban))
    app.add_handler(CommandHandler("unban", moderation.cmd_unban))
    app.add_handler(CommandHandler("mute", moderation.cmd_mute))
    app.add_handler(CommandHandler("unmute", moderation.cmd_unmute))
    app.add_handler(CommandHandler("warn", moderation.cmd_warn))
    app.add_handler(CommandHandler("unwarn", moderation.cmd_unwarn))
    app.add_handler(CommandHandler("warns", moderation.cmd_warns))

    # Gestion Groupe
    app.add_handler(CommandHandler("tagall", groups.cmd_tagall))
    app.add_handler(CommandHandler("leaderboard", groups.cmd_leaderboard_users))
    app.add_handler(CommandHandler("leaderboard_groups", groups.cmd_leaderboard_groups))
    app.add_handler(CommandHandler("stats", groups.cmd_stats_groupe))
    app.add_handler(CommandHandler("mystats", groups.cmd_mon_stats))
    app.add_handler(CommandHandler("reset_stats", groups.cmd_reset_stats))
    
    # Tracker les messages pour les statistiques
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, groups.track_message))

    print("Ziox Bot démarré 🚀")
    app.run_polling()


if __name__ == "__main__":
    main()
