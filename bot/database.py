"""
Base de données partagée entre le bot Telegram et l'API de la mini-app.
SQLite + SQLAlchemy : simple à déployer, largement suffisant pour démarrer.
Pour un vrai passage en production multi-serveurs, remplacer SQLite par PostgreSQL
(il suffit de changer DATABASE_URL, le code ORM ne change pas).
"""

import os
import time
import random
from datetime import datetime

from sqlalchemy import (
    create_engine, Column, Integer, BigInteger, String, Float, Boolean,
    DateTime, ForeignKey, Text, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ziox.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# ----------------------------------------------------------------------
# UTILISATEURS / PROFIL "LIFE CITY"
# ----------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)  # = telegram_id
    username = Column(String(64), nullable=True)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)

    # Profil "Life City"
    nom_affiche = Column(String(64), nullable=True)       # vrai nom choisi par le joueur
    nationalite = Column(String(64), nullable=True)
    age = Column(Integer, nullable=True)
    sexe = Column(String(16), nullable=True)               # "Homme" / "Femme" / "Autre"
    diplome = Column(String(128), nullable=True)
    statut_relationnel = Column(String(32), default="Célibataire")  # Célibataire / En couple / Marié(e)
    partenaire_id = Column(BigInteger, nullable=True)

    famille_id = Column(Integer, ForeignKey("familles.id"), nullable=True)

    date_creation = Column(DateTime, default=datetime.utcnow)
    profil_complet = Column(Boolean, default=False)

    famille = relationship("Famille", back_populates="membres")


# ----------------------------------------------------------------------
# BANQUE
# ----------------------------------------------------------------------

class CompteBancaire(Base):
    __tablename__ = "comptes"

    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    numero_compte = Column(String(20), unique=True)
    solde = Column(Float, default=200.0)  # capital de départ (ZCoins)
    solde_investi = Column(Float, default=0.0)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    expediteur_id = Column(BigInteger, nullable=True)   # null = généré par le système (coffre, gain de jeu...)
    destinataire_id = Column(BigInteger, nullable=False)
    montant = Column(Float, nullable=False)
    type = Column(String(32), default="virement")  # virement / coffre / jeu / bourse / famille
    note = Column(String(255), nullable=True)
    date = Column(DateTime, default=datetime.utcnow)


# ----------------------------------------------------------------------
# FAMILLE VIRTUELLE
# ----------------------------------------------------------------------

class Famille(Base):
    __tablename__ = "familles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(64), nullable=False)
    fondateur_id = Column(BigInteger, nullable=False)
    solde_commun = Column(Float, default=0.0)
    date_creation = Column(DateTime, default=datetime.utcnow)

    membres = relationship("User", back_populates="famille")


class InvitationFamille(Base):
    __tablename__ = "invitations_famille"

    id = Column(Integer, primary_key=True, autoincrement=True)
    famille_id = Column(Integer, ForeignKey("familles.id"))
    invite_id = Column(BigInteger, nullable=False)
    statut = Column(String(16), default="en_attente")  # en_attente / acceptee / refusee
    date = Column(DateTime, default=datetime.utcnow)


# ----------------------------------------------------------------------
# COFFRES & INVENTAIRE
# ----------------------------------------------------------------------

class Coffre(Base):
    __tablename__ = "coffres"

    user_id = Column(BigInteger, primary_key=True)
    dernier_ouverture = Column(Float, default=0.0)  # timestamp unix


class ObjetInventaire(Base):
    __tablename__ = "inventaire"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    categorie = Column(String(32))       # argent / voiture / objet_rare
    nom = Column(String(128))
    marque = Column(String(64), nullable=True)
    rarete = Column(String(16))          # commun / rare / épique / légendaire
    valeur = Column(Float, default=0.0)
    date_obtention = Column(DateTime, default=datetime.utcnow)


# ----------------------------------------------------------------------
# BOURSE SIMULÉE
# ----------------------------------------------------------------------

class ActifBoursier(Base):
    __tablename__ = "actifs"

    symbole = Column(String(12), primary_key=True)
    nom = Column(String(64))
    prix = Column(Float)
    volatilite = Column(Float, default=0.02)
    derniere_maj = Column(Float, default=0.0)  # timestamp unix


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    symbole = Column(String(12), ForeignKey("actifs.symbole"))
    quantite = Column(Float, default=0.0)
    prix_moyen_achat = Column(Float, default=0.0)


# ----------------------------------------------------------------------
# JEUX CONNECTÉS À LA BANQUE
# ----------------------------------------------------------------------

class Duel(Base):
    """Duel Pierre-Papier-Ciseaux avec mise, entre deux joueurs d'un groupe."""
    __tablename__ = "duels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False)
    challenger_id = Column(BigInteger, nullable=False)
    adversaire_id = Column(BigInteger, nullable=False)
    mise = Column(Float, nullable=False)

    statut = Column(String(16), default="en_attente")  # en_attente / en_cours / termine / refuse / annule
    choix_challenger = Column(String(16), nullable=True)   # pierre / feuille / ciseaux
    choix_adversaire = Column(String(16), nullable=True)

    gagnant_id = Column(BigInteger, nullable=True)
    date_creation = Column(DateTime, default=datetime.utcnow)


# ----------------------------------------------------------------------
# MODÉRATION
# ----------------------------------------------------------------------

class Avertissement(Base):
    __tablename__ = "avertissements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger)
    user_id = Column(BigInteger)
    raison = Column(String(255), nullable=True)
    date = Column(DateTime, default=datetime.utcnow)


# ----------------------------------------------------------------------
# PARAMÈTRES DE GROUPE (accueil / au revoir)
# ----------------------------------------------------------------------

class ParametresGroupe(Base):
    __tablename__ = "parametres_groupe"

    chat_id = Column(BigInteger, primary_key=True)

    accueil_actif = Column(Boolean, default=True)
    accueil_texte = Column(Text, default="✨ Bienvenue {prenom} dans {groupe} ! ✨")
    accueil_audio_file_id = Column(String(255), nullable=True)

    aurevoir_actif = Column(Boolean, default=True)
    aurevoir_texte = Column(Text, default="👋 {prenom} a quitté {groupe}. À bientôt !")
    aurevoir_audio_file_id = Column(String(255), nullable=True)


# ----------------------------------------------------------------------
# INITIALISATION
# ----------------------------------------------------------------------

ACTIFS_PAR_DEFAUT = [
    ("ZTC", "ZioxCoin", 25.0, 0.04),
    ("NRJ", "Energis Corp", 60.0, 0.03),
    ("AUTO", "MotorZ Industries", 120.0, 0.025),
    ("GOLD", "Or Virtuel", 300.0, 0.015),
    ("TECH", "NovaTech", 80.0, 0.05),
]


def init_db():
    Base.metadata.create_all(engine)
    session = SessionLocal()
    try:
        if session.query(ActifBoursier).count() == 0:
            for symbole, nom, prix, vol in ACTIFS_PAR_DEFAUT:
                session.add(ActifBoursier(
                    symbole=symbole, nom=nom, prix=prix,
                    volatilite=vol, derniere_maj=time.time()
                ))
            session.commit()
    finally:
        session.close()


def generer_numero_compte(user_id: int) -> str:
    return f"ZX{user_id % 100000000:08d}"


def get_or_create_user(session, telegram_user) -> User:
    user = session.get(User, telegram_user.id)
    if not user:
        user = User(
            id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=getattr(telegram_user, "last_name", None),
        )
        session.add(user)
        session.flush()
        session.add(CompteBancaire(
            user_id=user.id,
            numero_compte=generer_numero_compte(user.id),
            solde=200.0,
        ))
        session.add(Coffre(user_id=user.id, dernier_ouverture=0.0))
        session.commit()
    return user
