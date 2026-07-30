async def rules_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Commande /rules
    """

    chat = update.effective_chat

    group = await get_group(chat.id)

    if group is None:

        await update.message.reply_text(
            t("NO_RULES")
        )

        return

    rules = group["rules"]

    if not rules:

        await update.message.reply_text(
            t("NO_RULES")
        )

        return

    await update.message.reply_text(rules)
