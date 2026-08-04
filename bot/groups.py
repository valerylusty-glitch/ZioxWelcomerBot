"""
Système de gestion des groupes : kick all, tag all, leaderboard, statistiques.
Commandes admin pour gérer les groupes et afficher les classements.
"""

from telegram import Update, ChatPermissions
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from datetime import datetime, timedelta

from database import SessionLocal, GroupeStats, MessageStats, get_or_create_user, User
from moderation import est_admin


# ============================================================================
# OUTILS
# ============================================================================

async def maj_stats_groupe(context, chat_id: int, group_name: str):
    """Met à jour les statistiques du groupe."""
    session = SessionLocal()
    try:
        stats = session.get(GroupeStats, chat_id)
        if not stats:
            stats = GroupeStats(
                chat_id=chat_id,
                nom_groupe=group_name,
                total_messages=0,
                total_membres=0
            )
            session.add(stats)
        stats.derniere_maj = datetime.utcnow()
        session.commit()
    finally:
        session.close()


async def incrementer_messages(chat_id: int, user_id: int):
    """Incrémente le compteur de messages pour un utilisateur."""
    session = SessionLocal()
    try:
        stat = session.query(MessageStats).filter_by(
            chat_id=chat_id, user_id=user_id
        ).first()
        
        if not stat:
            stat = MessageStats(chat_id=chat_id, user_id=user_id, nombre_messages=1)
            session.add(stat)
        else:
            stat.nombre_messages += 1
            stat.date_derniers_messages = datetime.utcnow()
        
        session.commit()
    finally:
        session.close()


# ============================================================================
# COMMANDES ADMIN - GESTION GROUPE
# ============================================================================

async def cmd_kickall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Expulse tous les utilisateurs du groupe (sauf les admins)."""
    if not await est_admin(update, context):
        await update.message.reply_text("🚫 Réservé aux administrateurs.")
        return
    
    chat_id = update.effective_chat.id
    
    if not (context.args and context.args[0].lower() == "confirm"):
        # Message de confirmation
        await update.message.reply_text(
            "⚠️ *ATTENTION* ⚠️\n\n"
            "Vous êtes sur le point d'expulser *TOUS* les membres du groupe "
            "(sauf les administrateurs).\n\n"
            "Confirmez avec `/kickall confirm`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        # Récupérer tous les administrateurs
        admins = await context.bot.get_chat_administrators(chat_id)
        admin_ids = {admin.user.id for admin in admins}
        
        await update.message.reply_text(
            "⚠️ *Note:* Telegram ne permet pas d'obtenir la liste complète des membres.\n\n"
            "Pour expulser tous les membres:\n"
            "1. Créez un nouveau groupe\n"
            "2. Repartagez le lien d'invitation\n"
            "3. Supprimez l'ancien groupe\n\n"
            "Ou utilisez `/ban` sur chaque utilisateur individuellement.",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Erreur: {str(e)}")


async def cmd_tagall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mention tous les utilisateurs actifs du groupe."""
    chat_id = update.effective_chat.id
    
    if not context.args:
        await update.message.reply_text(
            "💬 *Mention tous*\n\n"
            "Utilisation: `/tagall <message>`\n"
            "Exemple: `/tagall Venez voir!`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    message_texte = " ".join(context.args)
    session = SessionLocal()
    
    try:
        # Récupérer les utilisateurs actifs du groupe
        stats = session.query(MessageStats).filter_by(chat_id=chat_id).all()
        
        if not stats:
            await update.message.reply_text("ℹ️ Aucun utilisateur actif à mentionner.")
            return
        
        # Limiter à 50 mentions (limite Telegram)
        users_to_mention = stats[:50]
        
        # Construire les mentions avec usernames ou IDs
        mentions_text = ""
        for stat in users_to_mention:
            user = session.get(User, stat.user_id)
            if user and user.username:
                mentions_text += f"@{user.username} "
            else:
                mentions_text += f"[User](tg://user?id={stat.user_id}) "
        
        texte_final = f"{mentions_text}\n\n{message_texte}"
        
        await update.message.reply_text(texte_final, parse_mode=ParseMode.MARKDOWN)
        
    finally:
        session.close()


async def cmd_leaderboard_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche le classement des utilisateurs les plus actifs."""
    chat_id = update.effective_chat.id
    session = SessionLocal()
    
    try:
        # Top 10 des utilisateurs les plus actifs
        top_users = session.query(MessageStats).filter_by(
            chat_id=chat_id
        ).order_by(MessageStats.nombre_messages.desc()).limit(10).all()
        
        if not top_users:
            await update.message.reply_text("📊 Aucune statistique disponible encore.")
            return
        
        texte = "╔════════════════════════════════╗\n"
        texte += "║ 🏆 *CLASSEMENT DES CHATTEURS* 🏆\n"
        texte += "╚════════════════════════════════╝\n\n"
        
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        for idx, stat in enumerate(top_users):
            user = session.get(User, stat.user_id)
            if user:
                username = f"@{user.username}" if user.username else f"User {stat.user_id}"
                first_name = user.first_name or "?"
                texte += f"{medals[idx]} *{first_name}* - *{stat.nombre_messages}* 💬\n"
            else:
                texte += f"{medals[idx]} *User {stat.user_id}* - *{stat.nombre_messages}* 💬\n"
        
        texte += f"\n📈 Mise à jour: {datetime.utcnow().strftime('%d/%m %H:%M')}"
        
        await update.message.reply_text(texte, parse_mode=ParseMode.MARKDOWN)
        
    finally:
        session.close()


async def cmd_leaderboard_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche le classement des groupes les plus actifs."""
    session = SessionLocal()
    
    try:
        # Compter les messages par groupe
        group_messages = {}
        all_stats = session.query(MessageStats).all()
        
        for stat in all_stats:
            if stat.chat_id not in group_messages:
                group_messages[stat.chat_id] = 0
            group_messages[stat.chat_id] += stat.nombre_messages
        
        if not group_messages:
            await update.message.reply_text("📊 Aucune statistique de groupe disponible.")
            return
        
        # Trier par nombre de messages
        sorted_groups = sorted(group_messages.items(), key=lambda x: x[1], reverse=True)[:10]
        
        texte = "╔════════════════════════════════╗\n"
        texte += "║ 🏆 *CLASSEMENT DES GROUPES* 🏆\n"
        texte += "╚════════════════════════════════╝\n\n"
        
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        for idx, (chat_id, total_messages) in enumerate(sorted_groups):
            group_stats = session.get(GroupeStats, chat_id)
            nom = group_stats.nom_groupe if group_stats else f"Groupe {chat_id}"
            
            # Compter les utilisateurs actifs
            active_users = session.query(MessageStats.user_id).filter_by(
                chat_id=chat_id
            ).distinct().count()
            
            texte += f"{medals[idx]} *{nom}*\n"
            texte += f"   └ {total_messages} messages • {active_users} actifs\n\n"
        
        texte += f"📈 Mise à jour: {datetime.utcnow().strftime('%d/%m %H:%M')}"
        
        await update.message.reply_text(texte, parse_mode=ParseMode.MARKDOWN)
        
    finally:
        session.close()


async def cmd_stats_groupe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche les statistiques du groupe."""
    chat_id = update.effective_chat.id
    group_name = update.effective_chat.title or "Groupe sans nom"
    session = SessionLocal()
    
    try:
        # Mise à jour des stats
        await maj_stats_groupe(context, chat_id, group_name)
        
        # Compter les messages
        total_messages = session.query(MessageStats).filter_by(
            chat_id=chat_id
        ).count()
        
        # Compter les utilisateurs actifs
        utilisateurs_actifs = session.query(MessageStats.user_id).filter_by(
            chat_id=chat_id
        ).distinct().count()
        
        # Nombre de messages du jour
        aujourd_hui = datetime.utcnow().date()
        messages_aujourd_hui = session.query(MessageStats).filter(
            MessageStats.chat_id == chat_id,
            MessageStats.date_derniers_messages >= datetime.combine(aujourd_hui, datetime.min.time())
        ).count()
        
        # Message par utilisateur en moyenne
        moyenne = total_messages / utilisateurs_actifs if utilisateurs_actifs > 0 else 0
        
        texte = "╔════════════════════════════════╗\n"
        texte += f"║ 📊 *STATS DE {group_name.upper()}*\n"
        texte += "╚════════════════════════════════╝\n\n"
        texte += f"📈 Total messages: *{total_messages}*\n"
        texte += f"👥 Utilisateurs actifs: *{utilisateurs_actifs}*\n"
        texte += f"📅 Aujourd'hui: *{messages_aujourd_hui}* messages\n"
        texte += f"💬 Moyenne par user: *{moyenne:.1f}* messages\n\n"
        texte += f"🕐 Dernière mise à jour: {datetime.utcnow().strftime('%H:%M:%S')}"
        
        await update.message.reply_text(texte, parse_mode=ParseMode.MARKDOWN)
        
    finally:
        session.close()


async def cmd_mon_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche tes statistiques personnelles."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_first_name = update.effective_user.first_name
    session = SessionLocal()
    
    try:
        stat = session.query(MessageStats).filter_by(
            chat_id=chat_id,
            user_id=user_id
        ).first()
        
        if not stat:
            await update.message.reply_text(f"ℹ️ {user_first_name}, tu n'as pas encore envoyé de messages ici.")
            return
        
        # Classement personnel
        ranking = session.query(MessageStats).filter_by(
            chat_id=chat_id
        ).filter(
            MessageStats.nombre_messages > stat.nombre_messages
        ).count() + 1
        
        # Pourcentage du total
        total_group = session.query(MessageStats).filter_by(chat_id=chat_id).count()
        pourcentage = (stat.nombre_messages / total_group * 100) if total_group > 0 else 0
        
        texte = "╔════════════════════════════════╗\n"
        texte += f"║ 👤 *TES STATS {user_first_name.upper()}*\n"
        texte += "╚════════════════════════════════╝\n\n"
        texte += f"💬 Messages: *{stat.nombre_messages}*\n"
        texte += f"🏆 Classement: *#{ranking}*\n"
        texte += f"📊 Pourcentage: *{pourcentage:.1f}%* du groupe\n"
        texte += f"📅 Dernier message: {stat.date_derniers_messages.strftime('%d/%m %H:%M')}\n"
        
        await update.message.reply_text(texte, parse_mode=ParseMode.MARKDOWN)
        
    finally:
        session.close()


async def cmd_reset_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Réinitialise les statistiques du groupe (admin seulement)."""
    if not await est_admin(update, context):
        await update.message.reply_text("🚫 Réservé aux administrateurs.")
        return
    
    chat_id = update.effective_chat.id
    session = SessionLocal()
    
    try:
        # Confirmation
        if not (context.args and context.args[0].lower() == "confirm"):
            await update.message.reply_text(
                "⚠️ Ceci réinitialisera *TOUTES* les statistiques du groupe.\n\n"
                "Confirmez avec `/reset_stats confirm`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Supprimer les stats
        session.query(MessageStats).filter_by(chat_id=chat_id).delete()
        session.query(GroupeStats).filter_by(chat_id=chat_id).delete()
        session.commit()
        
        await update.message.reply_text("✅ *Statistiques réinitialisées!*", parse_mode=ParseMode.MARKDOWN)
        
    finally:
        session.close()


async def cmd_top_this_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche le top des utilisateurs cette semaine."""
    chat_id = update.effective_chat.id
    session = SessionLocal()
    
    try:
        # Semaine dernière
        une_semaine_ago = datetime.utcnow() - timedelta(days=7)
        
        top_users = session.query(MessageStats).filter(
            MessageStats.chat_id == chat_id,
            MessageStats.date_derniers_messages >= une_semaine_ago
        ).order_by(MessageStats.nombre_messages.desc()).limit(10).all()
        
        if not top_users:
            await update.message.reply_text("📊 Aucune statistique pour cette semaine.")
            return
        
        texte = "╔════════════════════════════════╗\n"
        texte += "║ 🏆 *TOP CETTE SEMAINE* 🏆\n"
        texte += "╚════════════════════════════════╝\n\n"
        
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        for idx, stat in enumerate(top_users):
            user = session.get(User, stat.user_id)
            if user:
                first_name = user.first_name or "?"
                texte += f"{medals[idx]} *{first_name}* - *{stat.nombre_messages}* 💬\n"
            else:
                texte += f"{medals[idx]} *User {stat.user_id}* - *{stat.nombre_messages}* 💬\n"
        
        texte += f"\n📈 Du {une_semaine_ago.strftime('%d/%m')} au {datetime.utcnow().strftime('%d/%m')}"
        
        await update.message.reply_text(texte, parse_mode=ParseMode.MARKDOWN)
        
    finally:
        session.close()


# ============================================================================
# HELPER POUR INCRÉMENTER LES MESSAGES
# ============================================================================

async def track_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Suit chaque message pour les statistiques."""
    if update.effective_chat.type in ("group", "supergroup"):
        await incrementer_messages(update.effective_chat.id, update.effective_user.id)
