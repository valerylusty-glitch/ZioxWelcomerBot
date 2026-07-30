from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def captcha_keyboard(user_id: int):

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Je suis humain",
                callback_data=f"captcha:{user_id}"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)
