"""
utils/image.py

Création des cartes de bienvenue.
"""

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


CARD_WIDTH = 1000
CARD_HEIGHT = 500


def create_welcome_card(
    username: str,
    group: str,
):
    """
    Génère une carte de bienvenue.
    """

    background = Image.open(
        "assets/backgrounds/default.png"
    )

    background = background.resize(
        (CARD_WIDTH, CARD_HEIGHT)
    )

    draw = ImageDraw.Draw(background)

    title_font = ImageFont.truetype(
        "assets/fonts/Poppins-Bold.ttf",
        48,
    )

    subtitle_font = ImageFont.truetype(
        "assets/fonts/Poppins-Regular.ttf",
        32,
    )

    draw.text(
        (70, 70),
        "BIENVENUE",
        font=title_font,
        fill="white",
    )

    draw.text(
        (70, 150),
        username,
        font=subtitle_font,
        fill="white",
    )

    draw.text(
        (70, 210),
        group,
        font=subtitle_font,
        fill="white",
    )

    output = "assets/welcome_card.png"

    background.save(output)

    return output
