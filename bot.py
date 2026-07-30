"""
Bot Telegram Welcomer — avec menu de jeux et mini-application "Ziox".
Basé sur python-telegram-bot v21+ (async).

Démarrage : python bot.py
Configuration : voir .env.example
"""

import os
import random
import logging
from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    ChatMemberUpdated,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ChatMemberHandler,
    ContextTypes,
    filters,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "PLACE_TON_TOKEN_ICI")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://ton-domaine.exemple/webapp/index.html")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("ziox_bot")


# ----------------------------------------------------------------------
# TEXTES
# ----------------------------------------------------------------------

def texte_bienvenue(prenom: str) -> str:
    return (
        f"✨ <b>Bienvenue {prenom} !</b> ✨\n\n"
        "Je suis <b>Ziox Bot</b>, ton assistant sur ce chat.\n"
        "Voici ce que je peux faire pour toi :\n\n"
        "🎮 Des <b>mini-jeux</b> pour t'amuser\n"
        "🏙️ <b>Ziox</b>, ta ville virtuelle à faire grandir\n"
        "ℹ️ De l'aide à tout moment via /help\n\n"
        "Choisis une option ci-dessous 👇"
    )


def texte_accueil_groupe(prenom: str, groupe: str) -> str:
    return (
        f"🎉 <b>{prenom}</b> vient de rejoindre <b>{groupe}</b> !\n\n"
        "Bienvenue parmi nous, installe-toi confortablement ☕\n"
        "N'hésite pas à te présenter et à jeter un œil au règlement 📜"
    )


TEXTE_AIDE = (
    "🛠️ <b>Centre d'aide</b>\n\n"
    "/start — Afficher le menu principal\n"
    "/jeux — Ouvrir le menu des jeux\n"
    "/ziox — Lancer la mini-application Ziox\n"
    "/profil — Voir ton profil\n"
    "/help — Afficher ce message\n\n"
    "Besoin d'autre chose ? Utilise les boutons du menu 👇"
)


# ----------------------------------------------------------------------
# CLAVIERS
# ----------------------------------------------------------------------

def clavier_principal() -> InlineKeyboardMarkup:
    boutons = [
        [InlineKeyboardButton("🏙️ Ouvrir Ziox", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("🎮 Jeux", callback_data="menu_jeux")],
        [
            InlineKeyboardButton("👤 Profil", callback_data="menu_profil"),
            InlineKeyboardButton("ℹ️ Aide", callback_data="menu_aide"),
        ],
    ]
    return InlineKeyboardMarkup(boutons)


def clavier_jeux() -> InlineKeyboardMarkup:
    boutons = [
        [InlineKeyboardButton("🎲 Lancer un dé", callback_data="jeu_de")],
        [InlineKeyboardButton("✊✋✌️ Pierre-Papier-Ciseaux", callback_data="jeu_ppc")],
        [InlineKeyboardButton("🔢 Deviner le nombre", callback_data="jeu_deviner")],
        [InlineKeyboardButton("⬅️ Retour", callback_data="menu_accueil")],
    ]
    return InlineKeyboardMarkup(boutons)


def clavier_ppc() -> InlineKeyboardMarkup:
    boutons = [
        [
            InlineKeyboardButton("✊ Pierre", callback_data="ppc_pierre"),
            InlineKeyboardButton("✋ Feuille", callback_data="ppc_feuille"),
            InlineKeyboardButton("✌️ Ciseaux", callback_data="ppc_ciseaux"),
        ],
        [InlineKeyboardButton("⬅️ Retour", callback_data="menu_jeux")],
    ]
    return InlineKeyboardMarkup(boutons)


def clavier_retour(cible: str = "menu_accueil") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Retour", callback_data=cible)]]
    )


# ----------------------------------------------------------------------
# COMMANDES
# ----------------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    utilisateur = update.effective_user
    await update.message.reply_text(
        texte_bienvenue(utilisateur.first_name),
        parse_mode=ParseMode.HTML,
        reply_markup=clavier_principal(),
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXTE_AIDE, parse_mode=ParseMode.HTML)


async def cmd_jeux(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 <b>Choisis un jeu :</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=clavier_jeux(),
    )


async def cmd_ziox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏙️ Clique ci-dessous pour ouvrir <b>Ziox</b>, ta ville virtuelle !",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🚀 Lancer Ziox", web_app=WebAppInfo(url=WEBAPP_URL))]]
        ),
    )


async def cmd_profil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    texte = (
        "👤 <b>Ton profil</b>\n\n"
        f"Nom : {u.first_name} {u.last_name or ''}\n"
        f"Identifiant : @{u.username or 'non défini'}\n"
        f"ID Telegram : <code>{u.id}</code>"
    )
    await update.message.reply_text(texte, parse_mode=ParseMode.HTML)


# ----------------------------------------------------------------------
# ACCUEIL DES NOUVEAUX MEMBRES (GROUPE)
# ----------------------------------------------------------------------

async def accueil_nouveaux_membres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for membre in update.message.new_chat_members:
        if membre.is_bot:
            continue
        await update.message.reply_text(
            texte_accueil_groupe(membre.first_name, update.effective_chat.title or "ce groupe"),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("💬 Démarrer en privé", url=f"https://t.me/{context.bot.username}")]]
            ),
        )


# ----------------------------------------------------------------------
# JEUX — LOGIQUE
# ----------------------------------------------------------------------

async def jeu_de(query, context):
    await query.message.reply_dice(emoji="🎲")
    await query.answer("Bonne chance ! 🎲")


def resultat_ppc(choix_joueur: str, choix_bot: str) -> str:
    if choix_joueur == choix_bot:
        return "égalité"
    gagnant = {
        "pierre": "ciseaux",
        "feuille": "pierre",
        "ciseaux": "feuille",
    }
    return "joueur" if gagnant[choix_joueur] == choix_bot else "bot"


EMOJIS_PPC = {"pierre": "✊", "feuille": "✋", "ciseaux": "✌️"}


async def jeu_ppc_resultat(query, context, choix_joueur: str):
    choix_bot = random.choice(list(EMOJIS_PPC.keys()))
    issue = resultat_ppc(choix_joueur, choix_bot)

    if issue == "joueur":
        message_issue = "🏆 Tu as gagné !"
    elif issue == "bot":
        message_issue = "😅 J'ai gagné cette fois !"
    else:
        message_issue = "🤝 Égalité !"

    texte = (
        "✊✋✌️ <b>Pierre-Papier-Ciseaux</b>\n\n"
        f"Toi : {EMOJIS_PPC[choix_joueur]} {choix_joueur}\n"
        f"Moi : {EMOJIS_PPC[choix_bot]} {choix_bot}\n\n"
        f"{message_issue}"
    )
    await query.edit_message_text(
        texte, parse_mode=ParseMode.HTML, reply_markup=clavier_ppc()
    )


async def jeu_deviner_demarrer(query, context):
    context.user_data["nombre_secret"] = random.randint(1, 100)
    context.user_data["essais"] = 0
    await query.edit_message_text(
        "🔢 <b>Devine le nombre !</b>\n\n"
        "J'ai choisi un nombre entre 1 et 100.\n"
        "Envoie-moi ta proposition directement dans le chat 💬",
        parse_mode=ParseMode.HTML,
        reply_markup=clavier_retour("menu_jeux"),
    )


async def gerer_message_texte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les propositions du jeu 'Deviner le nombre'."""
    if "nombre_secret" not in context.user_data:
        return  # pas de partie en cours, on ignore

    texte = update.message.text.strip()
    if not texte.isdigit():
        await update.message.reply_text("Envoie un nombre valide 🙂")
        return

    proposition = int(texte)
    secret = context.user_data["nombre_secret"]
    context.user_data["essais"] += 1

    if proposition == secret:
        essais = context.user_data["essais"]
        await update.message.reply_text(
            f"🎉 <b>Bravo !</b> Tu as trouvé le nombre <b>{secret}</b> en {essais} essai(s) !",
            parse_mode=ParseMode.HTML,
            reply_markup=clavier_jeux(),
        )
        del context.user_data["nombre_secret"]
        del context.user_data["essais"]
    elif proposition < secret:
        await update.message.reply_text("📈 C'est plus grand !")
    else:
        await update.message.reply_text("📉 C'est plus petit !")


# ----------------------------------------------------------------------
# ROUTAGE DES BOUTONS (CALLBACK QUERY)
# ----------------------------------------------------------------------

async def gerer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "menu_accueil":
        await query.answer()
        await query.edit_message_text(
            texte_bienvenue(query.from_user.first_name),
            parse_mode=ParseMode.HTML,
            reply_markup=clavier_principal(),
        )

    elif data == "menu_jeux":
        await query.answer()
        await query.edit_message_text(
            "🎮 <b>Choisis un jeu :</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=clavier_jeux(),
        )

    elif data == "menu_aide":
        await query.answer()
        await query.edit_message_text(
            TEXTE_AIDE, parse_mode=ParseMode.HTML, reply_markup=clavier_retour()
        )

    elif data == "menu_profil":
        await query.answer()
        u = query.from_user
        texte = (
            "👤 <b>Ton profil</b>\n\n"
            f"Nom : {u.first_name} {u.last_name or ''}\n"
            f"Identifiant : @{u.username or 'non défini'}\n"
            f"ID Telegram : <code>{u.id}</code>"
        )
        await query.edit_message_text(
            texte, parse_mode=ParseMode.HTML, reply_markup=clavier_retour()
        )

    elif data == "jeu_de":
        await jeu_de(query, context)

    elif data == "jeu_ppc":
        await query.answer()
        await query.edit_message_text(
            "✊✋✌️ <b>Fais ton choix :</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=clavier_ppc(),
        )

    elif data.startswith("ppc_"):
        await query.answer()
        await jeu_ppc_resultat(query, context, data.replace("ppc_", ""))

    elif data == "jeu_deviner":
        await query.answer()
        await jeu_deviner_demarrer(query, context)

    else:
        await query.answer()


# ----------------------------------------------------------------------
# LANCEMENT
# ----------------------------------------------------------------------

def main():
    app: Application = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("jeux", cmd_jeux))
    app.add_handler(CommandHandler("ziox", cmd_ziox))
    app.add_handler(CommandHandler("profil", cmd_profil))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, accueil_nouveaux_membres))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gerer_message_texte))

    app.add_handler(CallbackQueryHandler(gerer_callback))

    logger.info("Ziox Bot démarré 🚀")
    app.run_polling()


if __name__ == "__main__":
    main()
        
