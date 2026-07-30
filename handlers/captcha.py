"""
handlers/captcha.py

Gestion du captcha.
"""

# ======================================================
# IMPORTS
# ======================================================

import asyncio

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ContextTypes,
)

from database import (
    create_captcha,
    delete_captcha,
    get_captcha,
    verify_captcha,
)

from keyboards.captcha import captcha_keyboard
from telegram import ChatPermissions


# ======================================================
# ENVOI DU CAPTCHA
# ======================================================

async def send_captcha(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message is None:
        return

    chat = update.effective_chat

    for member in update.message.new_chat_members:

        # Restriction de l'utilisateur
        await context.bot.restrict_chat_member(
            chat.id,
            member.id,
            permissions={}
        )

        message = await update.message.reply_text(
            (
                f"🤖 Bienvenue {member.mention_html()} !\n\n"
                "Clique sur le bouton ci-dessous dans les 60 secondes."
            ),
            parse_mode="HTML",
            reply_markup=captcha_keyboard(member.id),
        )

        await create_captcha(
            chat.id,
            member.id,
            message.message_id,
        )

        asyncio.create_task(
            captcha_timeout(
                context,
                chat.id,
                member.id,
            )
        )

# ======================================================
# TIMER
# ======================================================

async def captcha_timeout(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int,
):

    await asyncio.sleep(60)

    captcha = await get_captcha(
        chat_id,
        user_id,
    )

    if captcha is None:
        return

    if captcha["verified"]:
        return

    try:

        await context.bot.ban_chat_member(
            chat_id,
            user_id,
        )

        await context.bot.unban_chat_member(
            chat_id,
            user_id,
        )

    except Exception:
        pass

    await delete_captcha(
        chat_id,
        user_id,
    )

# ======================================================
# VALIDATION
# ======================================================

async def captcha_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    await query.answer()

    data = query.data

    if not data.startswith("captcha:"):
        return

    user_id = int(
        data.split(":")[1]
    )

    if query.from_user.id != user_id:

        await query.answer(
            "❌ Ce bouton ne t'appartient pas.",
            show_alert=True,
        )

        return

    chat_id = query.message.chat.id

    await verify_captcha(
        chat_id,
        user_id,
    )

  await context.bot.restrict_chat_member(
    chat_id,
    user_id,
    permissions=ChatPermissions(
        can_send_messages=True,
        can_send_other_messages=True,
        can_send_polls=True,
        can_add_web_page_previews=True,
        can_invite_users=True,
    ),
)
    )

    await query.edit_message_text(
        "✅ Vérification réussie !\nBienvenue !"
    )

    await delete_captcha(
        chat_id,
        user_id,
    )

# ======================================================
# REGISTER
# ======================================================

def register_captcha(app: Application):

    app.add_handler(
        CallbackQueryHandler(
            captcha_callback,
            pattern="^captcha:"
        )
    )
