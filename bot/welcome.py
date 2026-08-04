"""
Système d'accueil et d'au revoir personnalisable par groupe :
- Texte personnalisé (avec variables : {prenom}, {username}, {bio}, {groupe}, {user_id}, etc.)
- Affichage du profil utilisateur complet avec photo de profil
- Message vocal/audio personnalisé
- Activation / désactivation indépendante
- Support complet du Markdown Telegram
"""

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from database import SessionLocal, ParametresGroupe, get_or_create_user, User
from moderation import est_admin


def get_parametres(session, chat_id: int) -> ParametresGroupe:
    params = session.get(ParametresGroupe, chat_id)
    if not params:
        params = ParametresGroupe(chat_id=chat_id)
        session.add(params)
        session.commit()
    return params


def get_user_profile_text(session, member, user_id: int) -> str:
    """Génère un texte de profil esthétique avec toutes les infos de la base de données."""
    
    # Récupérer les infos du user depuis la base de données
    user = session.get(User, user_id)
    
    username = member.username or "N/A"
    first_name = member.first_name or "Utilisateur"
    last_name = member.last_name or ""
    
    # Infos du profil (si l'utilisateur existe en base)
    if user:
        nationalite = user.nationalite or "Non renseignée"
        age = user.age or "Non renseigné"
        sexe = user.sexe or "Non renseigné"
        diplome = user.diplome or "Non renseigné"
        statut = user.statut_relationnel or "Non renseigné"
    else:
        nationalite = "Non renseignée"
        age = "Non renseigné"
        sexe = "Non renseigné"
        diplome = "Non renseigné"
        statut = "Non renseigné"
    
    profile_text = (
        "┌─────────────────────────────┐\n"
        f"│ 👤 *{first_name} {last_name}*\n"
        f"│ └ @{username}\n"
        f"│ ID: `{user_id}`\n"
        f"│\n"
        f"│ 🌍 Nationalité: *{nationalite}*\n"
        f"│ 🎂 Âge: *{age}*\n"
        f"│ ⚧ Sexe: *{sexe}*\n"
        f"│ 🎓 Diplôme: *{diplome}*\n"
        f"│ 💞 Statut: *{statut}*\n"
        "└─────────────────────────────┘"
    )
    
    return profile_text


async def get_user_photo(context, user_id: int):
    """Récupère la photo de profil de l'utilisateur."""
    try:
        photos = await context.bot.get_user_profile_photos(user_id=user_id, limit=1)
        if photos.photos:
            return photos.photos[0][0].file_id
    except Exception as e:
        print(f"Erreur lors de la récupération de la photo: {e}")
    return None


def format_welcome_message(member, group_name: str, custom_template: str = None) -> str:
    """Formate le message d'accueil avec variables."""
    if custom_template is None:
        custom_template = (
            "╔════════════════════════════╗\n"
            "║ ✨ *BIENVENUE* ✨\n"
            "╚════════════════════════════╝\n\n"
            "{user_profile}\n\n"
            "Bienvenue *{prenom}* dans le groupe *{groupe}* 🎉\n"
            "Nous sommes heureux de t'accueillir !"
        )
    
    message = custom_template.format(
        prenom=member.first_name or "ami",
        username=member.username or "utilisateur",
        groupe=group_name,
        user_id=member.id,
    )
    
    return message


def format_goodbye_message(member, group_name: str, custom_template: str = None) -> str:
    """Formate le message d'au revoir avec variables."""
    if custom_template is None:
        custom_template = (
            "╔════════════════════════════╗\n"
            "║ 👋 *AU REVOIR* 👋\n"
            "╚════════════════════════════╝\n\n"
            "{user_profile}\n\n"
            "*{prenom}* a quitté le groupe *{groupe}*\n"
            "À bientôt ! 😢"
        )
    
    message = custom_template.format(
        prenom=member.first_name or "ami",
        username=member.username or "utilisateur",
        groupe=group_name,
        user_id=member.id,
    )
    
    return message


# ----------------------------------------------------------------------
# COMMANDES DE CONFIGURATION (admin uniquement)
# ----------------------------------------------------------------------

async def cmd_accueil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await est_admin(update, context):
        await update.message.reply_text("🚫 Réservé aux administrateurs.")
        return

    if not context.args:
        help_text = (
            "ℹ️ *Configuration de l'accueil*\n\n"
            "`/accueil on` | `off` — activer / désactiver\n"
            "`/accueil texte <message>` — définir le texte\n\n"
            "*Variables disponibles:*\n"
            "`{prenom}` — Prénom\n"
            "`{username}` — Username\n"
            "`{groupe}` — Nom du groupe\n"
            "`{user_id}` — ID utilisateur\n"
            "`{user_profile}` — Profil complet avec infos\n\n"
            "`/accueil audio` — répondre à un vocal\n"
            "`/accueil test` — prévisualiser le message"
        )
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
        return

    sous_commande = context.args[0].lower()
    session = SessionLocal()
    try:
        params = get_parametres(session, update.effective_chat.id)

        if sous_commande == "on":
            params.accueil_actif = True
            session.commit()
            await update.message.reply_text(
                "✅ *Accueil activé*",
                parse_mode=ParseMode.MARKDOWN
            )

        elif sous_commande == "off":
            params.accueil_actif = False
            session.commit()
            await update.message.reply_text(
                "🔕 *Accueil désactivé*",
                parse_mode=ParseMode.MARKDOWN
            )

        elif sous_commande == "texte":
            nouveau_texte = update.message.text.split(maxsplit=2)
            if len(nouveau_texte) < 3:
                await update.message.reply_text(
                    "ℹ️ Utilisation: `/accueil texte Bienvenue {prenom} dans {groupe}!`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            params.accueil_texte = nouveau_texte[2]
            session.commit()
            await update.message.reply_text(
                "✅ *Texte d'accueil mis à jour*",
                parse_mode=ParseMode.MARKDOWN
            )

        elif sous_commande == "audio":
            if not update.message.reply_to_message or not (
                update.message.reply_to_message.voice or update.message.reply_to_message.audio
            ):
                await update.message.reply_text(
                    "ℹ️ Réponds à un message vocal/audio avec `/accueil audio`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            media = update.message.reply_to_message.voice or update.message.reply_to_message.audio
            params.accueil_audio_file_id = media.file_id
            session.commit()
            await update.message.reply_text(
                "✅ *Audio d'accueil enregistré*",
                parse_mode=ParseMode.MARKDOWN
            )

        elif sous_commande == "test":
            user_profile = get_user_profile_text(session, update.effective_user, update.effective_user.id)
            texte = format_welcome_message(
                update.effective_user,
                update.effective_chat.title or "ce groupe",
                params.accueil_texte
            )
            texte = texte.replace("{user_profile}", user_profile)
            
            # Essayer d'envoyer avec photo de profil
            photo_id = await get_user_photo(context, update.effective_user.id)
            
            if photo_id:
                await update.message.reply_photo(
                    photo=photo_id,
                    caption=texte,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(texte, parse_mode=ParseMode.MARKDOWN)
            
            if params.accueil_audio_file_id:
                await update.message.reply_voice(params.accueil_audio_file_id)

        else:
            await update.message.reply_text(
                "ℹ️ Sous-commande inconnue. Utilise `/accueil` pour l'aide.",
                parse_mode=ParseMode.MARKDOWN
            )
    finally:
        session.close()


async def cmd_aurevoir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await est_admin(update, context):
        await update.message.reply_text("🚫 Réservé aux administrateurs.")
        return

    if not context.args:
        help_text = (
            "ℹ️ *Configuration de l'au revoir*\n\n"
            "`/aurevoir on` | `off` — activer / désactiver\n"
            "`/aurevoir texte <message>` — définir le texte\n\n"
            "*Variables disponibles:*\n"
            "`{prenom}` — Prénom\n"
            "`{username}` — Username\n"
            "`{groupe}` — Nom du groupe\n"
            "`{user_id}` — ID utilisateur\n"
            "`{user_profile}` — Profil complet avec infos\n\n"
            "`/aurevoir audio` — répondre à un vocal\n"
            "`/aurevoir test` — prévisualiser le message"
        )
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
        return

    sous_commande = context.args[0].lower()
    session = SessionLocal()
    try:
        params = get_parametres(session, update.effective_chat.id)

        if sous_commande == "on":
            params.aurevoir_actif = True
            session.commit()
            await update.message.reply_text(
                "✅ *Au revoir activé*",
                parse_mode=ParseMode.MARKDOWN
            )

        elif sous_commande == "off":
            params.aurevoir_actif = False
            session.commit()
            await update.message.reply_text(
                "🔕 *Au revoir désactivé*",
                parse_mode=ParseMode.MARKDOWN
            )

        elif sous_commande == "texte":
            nouveau_texte = update.message.text.split(maxsplit=2)
            if len(nouveau_texte) < 3:
                await update.message.reply_text(
                    "ℹ️ Utilisation: `/aurevoir texte À bientôt {prenom}!`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            params.aurevoir_texte = nouveau_texte[2]
            session.commit()
            await update.message.reply_text(
                "✅ *Texte d'au revoir mis à jour*",
                parse_mode=ParseMode.MARKDOWN
            )

        elif sous_commande == "audio":
            if not update.message.reply_to_message or not (
                update.message.reply_to_message.voice or update.message.reply_to_message.audio
            ):
                await update.message.reply_text(
                    "ℹ️ Réponds à un message vocal/audio avec `/aurevoir audio`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            media = update.message.reply_to_message.voice or update.message.reply_to_message.audio
            params.aurevoir_audio_file_id = media.file_id
            session.commit()
            await update.message.reply_text(
                "✅ *Audio d'au revoir enregistré*",
                parse_mode=ParseMode.MARKDOWN
            )

        elif sous_commande == "test":
            user_profile = get_user_profile_text(session, update.effective_user, update.effective_user.id)
            texte = format_goodbye_message(
                update.effective_user,
                update.effective_chat.title or "ce groupe",
                params.aurevoir_texte
            )
            texte = texte.replace("{user_profile}", user_profile)
            
            # Essayer d'envoyer avec photo de profil
            photo_id = await get_user_photo(context, update.effective_user.id)
            
            if photo_id:
                await update.message.reply_photo(
                    photo=photo_id,
                    caption=texte,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(texte, parse_mode=ParseMode.MARKDOWN)
            
            if params.aurevoir_audio_file_id:
                await update.message.reply_voice(params.aurevoir_audio_file_id)

        else:
            await update.message.reply_text(
                "ℹ️ Sous-commande inconnue. Utilise `/aurevoir` pour l'aide.",
                parse_mode=ParseMode.MARKDOWN
            )
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
        
        group_name = update.effective_chat.title or "ce groupe"
        
        for membre in update.message.new_chat_members:
            if membre.is_bot:
                continue
            
            # Créer/récupérer l'utilisateur en base de données
            get_or_create_user(session, membre)
            
            user_profile = get_user_profile_text(session, membre, membre.id)
            texte = format_welcome_message(membre, group_name, params.accueil_texte)
            texte = texte.replace("{user_profile}", user_profile)
            
            # Essayer d'envoyer avec photo de profil
            photo_id = await get_user_photo(context, membre.id)
            
            if photo_id:
                await update.message.reply_photo(
                    photo=photo_id,
                    caption=texte,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(texte, parse_mode=ParseMode.MARKDOWN)
            
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
        
        group_name = update.effective_chat.title or "ce groupe"
        user_profile = get_user_profile_text(session, membre, membre.id)
        texte = format_goodbye_message(membre, group_name, params.aurevoir_texte)
        texte = texte.replace("{user_profile}", user_profile)
        
        # Essayer d'envoyer avec photo de profil
        photo_id = await get_user_photo(context, membre.id)
        
        if photo_id:
            await update.message.reply_photo(
                photo=photo_id,
                caption=texte,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(texte, parse_mode=ParseMode.MARKDOWN)
        
        if params.aurevoir_audio_file_id:
            await update.message.reply_voice(params.aurevoir_audio_file_id)
    finally:
        session.close()
