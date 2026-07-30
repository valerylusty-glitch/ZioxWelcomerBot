"""
utils/image.py
Création des cartes de bienvenue avec photo de profil.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

CARD_WIDTH = 1000
CARD_HEIGHT = 500
AVATAR_SIZE = (250, 250)

def create_welcome_card(
    username: str,
    group: str,
    avatar_path: str = None
):
    """
    Génère une carte de bienvenue avec avatar optionnel.
    """
    # Ouvrir le fond
    background = Image.open("assets/backgrounds/default.png")
    background = background.resize((CARD_WIDTH, CARD_HEIGHT))
    
    # Créer un masque pour l'avatar circulaire
    mask = Image.new('L', AVATAR_SIZE, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0) + AVATAR_SIZE, fill=255)
    
    # Traiter l'avatar si présent
    if avatar_path and os.path.exists(avatar_path):
        try:
            avatar = Image.open(avatar_path).convert("RGBA")
            avatar = ImageOps.fit(avatar, AVATAR_SIZE, centering=(0.5, 0.5))
            
            # Appliquer le masque circulaire
            circular_avatar = Image.new("RGBA", AVATAR_SIZE, (0, 0, 0, 0))
            circular_avatar.paste(avatar, (0, 0), mask)
            
            # Coller l'avatar sur le fond (position à droite)
            background.paste(circular_avatar, (650, 125), circular_avatar)
        except Exception as e:
            print(f"Erreur traitement avatar: {e}")

    draw = ImageDraw.Draw(background)
    
    try:
        title_font = ImageFont.truetype("assets/fonts/Poppins-Bold.ttf", 60)
        name_font = ImageFont.truetype("assets/fonts/Poppins-Bold.ttf", 45)
        subtitle_font = ImageFont.truetype("assets/fonts/Poppins-Regular.ttf", 35)
    except:
        title_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # Textes à gauche
    draw.text((70, 120), "BIENVENUE", font=title_font, fill="#FFFFFF")
    draw.text((70, 210), username, font=name_font, fill="#FFD700") 
    draw.text((70, 280), f"dans {group}", font=subtitle_font, fill="#E0E0E0")

    output = "assets/welcome_card.png"
    background.save(output)
    return output
