"""
utils/permissions.py

Gestion des permissions.
"""

# ======================================================
# IMPORTS
# ======================================================

from telegram import Update


# ======================================================
# ADMIN
# ======================================================

async def is_admin(update: Update) -> bool:
    """
    Vérifie si l'utilisateur est administrateur.
    """

    if update.effective_chat is None:
        return False

    if update.effective_user is None:
        return False

    member = await update.effective_chat.get_member(
        update.effective_user.id
    )

    from utils.constants import ADMIN_ROLES (
        "administrator",
        "creator",
    )
    return member.status in ADMIN_ROLES
