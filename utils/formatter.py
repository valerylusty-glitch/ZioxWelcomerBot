"""
utils/formatter.py

Formatage des messages.
"""


def format_welcome(
    message: str,
    user: str,
    group: str,
) -> str:
    """
    Remplace les variables du message de bienvenue.
    """

    return (
        message
        .replace("{user}", user)
        .replace("{group}", group)
    )


def format_goodbye(
    message: str,
    user: str,
    group: str,
) -> str:
    """
    Remplace les variables du message d'au revoir.
    """

    return (
        message
        .replace("{user}", user)
        .replace("{group}", group)
    )
