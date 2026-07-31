"""
Jeux connectés à la banque Ziox : machine à sous (solo) et duel Pierre-Papier-Ciseaux.
Chaque jeu débite/credite de vraies ZCoins via la table CompteBancaire.
"""
import random
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from database import SessionLocal, get_or_create_user, CompteBancaire, Duel

# ----------------------------------------------------------------------
# MACHINE À SOUS
# ----------------------------------------------------------------------
SYMBOLS = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣"]

async def cmd_machine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Machine à sous : mise minimale 5 ZCoins, jackpot x25 sur triple 7️⃣."""
    if not context.args or not context.args[0].replace(".", "").isdigit():
        await update.message.reply_text("ℹ️ Utilisation : /machine <mise> (minimum 5 ZCoins)")
        return

    mise = float(context.args[0])
    if mise < 5:
        await update.message.reply_text("⚠️ Mise minimale : 5 ZCoins.")
        return

    session = SessionLocal()
    try:
        user = get_or_create_user(session, update.effective_user)
        compte = session.get(CompteBancaire, user.id)

        if compte.solde < mise:
            await update.message.reply_text("❌ Solde insuffisant pour cette mise.")
            return

        compte.solde -= mise
        session.commit()

        rouleaux = [random.choice(SYMBOLS) for _ in range(3)]
        resultat = " | ".join(rouleaux)

        if rouleaux.count("7️⃣") == 3:
            gain = mise * 25
            compte.solde += gain
            session.commit()
            await update.message.reply_text(
                f"🎰 <b>JACKPOT !!!</b>\n\n{resultat}\n\n"
                f"🏆 Tu gagnes <b>{gain:.0f} ZCoins</b> !",
                parse_mode=ParseMode.HTML,
            )
        elif len(set(rouleaux)) == 1:
            gain = mise * 10
            compte.solde += gain
            session.commit()
            await update.message.reply_text(
                f"🎰 <b>TRIPLE !</b>\n\n{resultat}\n\n"
                f"🎉 Tu gagnes <b>{gain:.0f} ZCoins</b> !",
                parse_mode=ParseMode.HTML,
            )
        elif len(set(rouleaux)) == 2:
            gain = mise * 2
            compte.solde += gain
            session.commit()
            await update.message.reply_text(
                f"🎰 <b>Paire !</b>\n\n{resultat}\n\n"
                f"💸 Tu gagnes <b>{gain:.0f} ZCoins</b> !",
                parse_mode=ParseMode.HTML,
            )
        else:
            session.commit()
            await update.message.reply_text(
                f"🎰 {resultat}\n\n"
                f"😢 Perdu... Mise de <b>{mise:.0f} ZCoins</b>.\n"
                f"Nouveau solde : <b>{compte.solde:.0f} ZCoins</b>",
                parse_mode=ParseMode.HTML,
            )
    finally:
        session.close()


# ----------------------------------------------------------------------
# DUEL PIERRE-PAPIER-CISEAUX
# ----------------------------------------------------------------------
async def cmd_duel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Défi Pierre-Papier-Ciseaux avec mise. Répondre au message de l'adversaire."""
    if not context.args or not context.args[0].replace(".", "").isdigit():
        await update.message.reply_text("ℹ️ Utilisation : /duel <mise> (répondre au message de l'adversaire)")
        return

    mise = float(context.args[0])
    if mise < 5:
        await update.message.reply_text("⚠️ Mise minimale : 5 ZCoins.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("ℹ️ Réponds au message de ton adversaire avec /duel <mise>.")
        return

    adversaire = update.message.reply_to_message.from_user
    if adversaire.is_bot:
        await update.message.reply_text("❌ Tu ne peux pas défier un bot.")
        return

    session = SessionLocal()
    try:
        challenger = get_or_create_user(session, update.effective_user)
        compte_challenger = session.get(CompteBancaire, challenger.id)

        if compte_challenger.solde < mise:
            await update.message.reply_text("❌ Solde insuffisant pour cette mise.")
            return

        duel = Duel(
            chat_id=update.effective_chat.id,
            challenger_id=challenger.id,
            adversaire_id=adversaire.id,
            mise=mise,
            statut="en_attente",
        )
        session.add(duel)
        session.commit()

        clavier = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚔️ Accepter le duel", callback_data=f"duel_accepter_{duel.id}")],
            [InlineKeyboardButton("❌ Refuser", callback_data=f"duel_refuser_{duel.id}")],
        ])

        await update.message.reply_text(
            f"⚔️ <b>Duel !</b>\n\n"
            f"{update.effective_user.first_name} défie <b>{adversaire.first_name}</b> !\n"
            f"💰 Mise : <b>{mise:.0f} ZCoins</b>\n\n"
            f"<b>{adversaire.first_name}</b>, accepte ou refuse le duel 👇",
            parse_mode=ParseMode.HTML,
            reply_markup=clavier,
        )
    finally:
        session.close()


async def gerer_callback_duel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les callbacks : acceptation, choix des joueurs, résolution."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    action = parts[1]
    duel_id = int(parts[2])

    session = SessionLocal()
    try:
        duel = session.get(Duel, duel_id)
        if not duel:
            await query.edit_message_text("❌ Duel introuvable.")
            return

        if action == "accepter":
            if query.from_user.id != duel.adversaire_id:
                await query.answer("Ce duel ne t'est pas destiné.", show_alert=True)
                return

            duel.statut = "en_cours"
            session.commit()

            clavier = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🪨 Pierre", callback_data=f"duel_choix_{duel_id}_pierre"),
                    InlineKeyboardButton("📄 Papier", callback_data=f"duel_choix_{duel_id}_papier"),
                    InlineKeyboardButton("✂️ Ciseaux", callback_data=f"duel_choix_{duel.id}_ciseaux"),
                ],
            ])

            await query.edit_message_text(
                f"⚔️ <b>Duel accepté !</b>\n\n"
                f"Mise : <b>{duel.mise:.0f} ZCoins</b>\n\n"
                f"Chacun choisit en secret 🤫",
                parse_mode=ParseMode.HTML,
                reply_markup=clavier,
            )

        elif action == "refuser":
            if query.from_user.id != duel.adversaire_id:
                await query.answer("Ce duel ne t'est pas destiné.", show_alert=True)
                return

            duel.statut = "refuse"
            session.commit()
            await query.edit_message_text("❌ Duel refusé.")

        elif action == "choix":
            choix = parts[3]
            # Enregistrer le choix du joueur
            if query.from_user.id == duel.challenger_id:
                duel.choix_challenger = choix
            elif query.from_user.id == duel.adversaire_id:
                duel.choix_adversaire = choix
            else:
                await query.answer("Tu ne fais pas partie de ce duel.", show_alert=True)
                return

            session.commit()
            await query.answer("Choix enregistré ! 🤫", show_alert=True)

            # Si les deux ont choisi, résoudre le duel
            if duel.choix_challenger and duel.choix_adversaire:
                _resoudre_duel(session, duel)
                await query.edit_message_text("✅ Les deux joueurs ont choisi ! Résultat en cours...")
                # Envoyer le résultat
                _envoyer_resultat_duel(context, duel, update.effective_chat.id)

        else:
            await query.answer("Action inconnue.", show_alert=True)
    finally:
        session.close()


def _resoudre_duel(session, duel: Duel):
    """Détermine le gagnant du duel et transfère les ZCoins."""
    choix = {"pierre": "ciseaux", "papier": "pierre", "ciseaux": "papier"}

    if duel.choix_challenger == duel.choix_adversaire:
        duel.gagnant_id = None  # égalité
        duel.statut = "termine"
        session.commit()
        return

    if choix[duel.choix_challenger] == duel.choix_adversaire:
        duel.gagnant_id = duel.challenger_id
    else:
        duel.gagnant_id = duel.adversaire_id

    duel.statut = "termine"

    # Transférer la mise
    gagnant = session.get(CompteBancaire, duel.gagnant_id)
    if duel.gagnant_id == duel.challenger_id:
        perdant = session.get(CompteBancaire, duel.adversaire_id)
    else:
        perdant = session.get(CompteBancaire, duel.challenger_id)

    gagnant.solde += duel.mise
    perdant.solde -= duel.mise
    session.commit()


def _envoyer_resultat_duel(context, duel: Duel, chat_id: int):
    """Envoie le résultat du duel dans le chat."""
    noms = {duel.challenger_id: "Joueur 1", duel.adversaire_id: "Joueur 2"}

    resultat = (
        f"⚔️ <b>Résultat du duel !</b>\n\n"
        f"🪨 vs 📄 vs ✂️\n\n"
        f"Joueur 1 ({noms[duel.challenger_id]}) : <b>{duel.choix_challenger}</b>\n"
        f"Joueur 2 ({noms[duel.adversaire_id]}) : <b>{duel.choix_adversaire}</b>\n\n"
    )

    if duel.gagnant_id:
        session = SessionLocal()
        try:
            gagnant_tg = session.get(CompteBancaire, duel.gagnant_id)
            gagnant_compte = session.get(CompteBancaire, duel.gagnant_id)
            gagnant_user = session.query(
                __import__("database", fromlist=["User"]).User
            ).get(duel.gagnant_id)
            gagnant_nom = gagnant_user.first_name if gagnant_user else "Inconnu"
        finally:
            session.close()

        resultat += (
            f"🏆 <b>{gagnant_nom}</b> remporte <b>{duel.mise:.0f} ZCoins</b> !"
        )
    else:
        resultat += "🤝 Égalité ! La mise est restituée."

    from telegram.ext import ContextTypes
    context.bot.send_message(chat_id=chat_id, text=resultat, parse_mode=ParseMode.HTML)
