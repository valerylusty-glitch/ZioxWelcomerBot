@admin_only
async def unmute_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.message.reply_to_message:

        await update.message.reply_text(
            "⚠️ Réponds au message."
        )

        return

    user = update.message.reply_to_message.from_user

    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_change_info=False,
        can_invite_users=True,
        can_pin_messages=False,
    )

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        permissions=permissions,
    )

    await update.message.reply_text(
        f"🔊 {user.full_name} peut à nouveau parler."
    )
