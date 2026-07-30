@admin_only
async def kick_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.message.reply_to_message:

        await update.message.reply_text(
            "⚠️ Réponds au message de l'utilisateur."
        )

        return

    user = update.message.reply_to_message.from_user

    try:

        await context.bot.ban_chat_member(
            update.effective_chat.id,
            user.id,
        )

        await context.bot.unban_chat_member(
            update.effective_chat.id,
            user.id,
        )

        await update.message.reply_text(
            f"👢 {user.full_name} a été expulsé."
        )

    except Exception as e:

        await update.message.reply_text(str(e))
