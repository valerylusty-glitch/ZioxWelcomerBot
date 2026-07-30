"""
utils/logger.py

Configuration du système de logs.
"""

# ======================================================
# IMPORTS
# ======================================================

import logging

from config import LOG_LEVEL


# ======================================================
# CONFIGURATION
# ======================================================

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
)

logger = logging.getLogger("ZioxWelcomer")
