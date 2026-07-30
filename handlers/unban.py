@admin_only
async def unban_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not context.args:

        await update.message.reply_text(
            "Utilisation : /unban <user_id>"
        )

        return

    user_id = int(context.args[0])

    await context.bot.unban_chat_member(
        update.effective_chat.id,
        user_id,
    )

    await update.message.reply_text(
        "✅ Utilisateur débanni."
    )
