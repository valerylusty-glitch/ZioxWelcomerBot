"""
handlers/__init__.py

Enregistre tous les handlers du bot.
"""

# ======================================================
# IMPORTS
# ======================================================

from telegram.ext import Application

from .commands import register_commands
from .welcome import register_welcome
from .goodbye import register_goodbye
from .admin import register_admin
from .callbacks import register_callbacks
from .moderation import register_moderation
from .member import register_member


# ======================================================
# REGISTER
# ======================================================

def register_handlers(app: Application):

    register_commands(app)

    register_welcome(app)

    register_goodbye(app)

    register_admin(app)

    register_callbacks(app)
    
    register_moderation(app)
    
    register_member(app)
