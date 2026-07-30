"""
locales/__init__.py
"""

from config import LANGUAGE

from .fr import MESSAGES as FR
from .en import MESSAGES as EN


LANGUAGES = {
    "fr": FR,
    "en": EN,
}


def t(key: str) -> str:
    """
    Retourne un texte selon la langue configurée.
    """

    language = LANGUAGES.get(
        LANGUAGE,
        FR,
    )

    return language.get(key, key)
