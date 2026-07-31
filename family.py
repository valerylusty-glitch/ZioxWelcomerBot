"""
Système de reconnaissance familiale : créer une famille, inviter des membres,
accepter une invitation dans le groupe.
"""

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from database import SessionLocal, Famille, InvitationFamille, get_or_create_user


async def cmd_famille(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()
    try:
        utilisateur = get_or_create_user(session, update.effective_user)

        if not context.args:
            if utilisateur.famille_id:
                famille = session.get(Famille, utilisateur.famille_id)
                membres = session.query(Famille).get(famille.id).membres
                noms = ", ".join(m.first_name or str(m.id) for m in membres)
                await update.message.reply_text(
                    f"👨‍👩‍👧‍👦 <b>Famille {famille.nom}</b>\n\n"
                    f"Membres : {noms}\n"
                    f"💰 Solde commun : {famille.solde_commun:.0f} ZCoins\n\n"
                    "Commandes : /famille inviter (en réponse à un message) · /famille quitter",
                    parse_mode=ParseMode.HTML,
                )
            else:
                await update.message.reply_text(
                    "ℹ️ <b>Système de famille</b>\n\n"
                    "/famille creer &lt;nom&gt; — fonder une famille\n"
                    "/famille inviter — répondre au message d'un membre pour l'inviter\n"
                    "/famille accepter — accepter une invitation en attente\n"
                    "/famille quitter — quitter ta famille actuelle",
                    parse_mode=ParseMode.HTML,
                )
            return

        sous_commande = context.args[0].lower()

        if sous_commande == "creer":
            if utilisateur.famille_id:
                await update.message.reply_text("Tu fais déjà partie d'une famille. Quitte-la d'abord avec /famille quitter.")
                return
            nom = " ".join(context.args[1:]) or f"Famille de {update.effective_user.first_name}"
            famille = Famille(nom=nom, fondateur_id=utilisateur.id)
            session.add(famille)
            session.flush()
            utilisateur.famille_id = famille.id
            session.commit()
            await update.message.reply_text(
                f"🏡 Famille <b>{nom}</b> fondée avec succès ! Invite des membres avec /famille inviter.",
                parse_mode=ParseMode.HTML,
            )

        elif sous_commande == "inviter":
            if not utilisateur.famille_id:
                await update.message.reply_text("Tu dois d'abord fonder une famille avec /famille creer <nom>.")
                return
            if not update.message.reply_to_message:
                await update.message.reply_text("ℹ️ Réponds au message de la personne à inviter avec /famille inviter.")
                return
            cible_tg = update.message.reply_to_message.from_user
            cible = get_or_create_user(session, cible_tg)
            if cible.famille_id:
                await update.message.reply_text(f"{cible.first_name} appartient déjà à une famille.")
                return
            invitation = InvitationFamille(famille_id=utilisateur.famille_id, invite_id=cible.id)
            session.add(invitation)
            session.commit()
            await update.message.reply_text(
                f"💌 Invitation envoyée à <b>{cible.first_name}</b> ! "
                f"Il/elle peut l'accepter avec /famille accepter.",
                parse_mode=ParseMode.HTML,
            )

        elif sous_commande == "accepter":
            invitation = (
                session.query(InvitationFamille)
                .filter_by(invite_id=utilisateur.id, statut="en_attente")
                .order_by(InvitationFamille.id.desc())
                .first()
            )
            if not invitation:
                await update.message.reply_text("Tu n'as aucune invitation en attente.")
                return
            invitation.statut = "acceptee"
            utilisateur.famille_id = invitation.famille_id
            session.commit()
            famille = session.get(Famille, invitation.famille_id)
            await update.message.reply_text(
                f"🎉 Bienvenue dans la famille <b>{famille.nom}</b> !", parse_mode=ParseMode.HTML
            )

        elif sous_commande == "quitter":
            if not utilisateur.famille_id:
                await update.message.reply_text("Tu ne fais partie d'aucune famille.")
                return
            utilisateur.famille_id = None
            session.commit()
            await update.message.reply_text("👋 Tu as quitté ta famille.")

        else:
            await update.message.reply_text("ℹ️ Sous-commande inconnue. Utilise /famille sans argument pour l'aide.")

    finally:
        session.close()
