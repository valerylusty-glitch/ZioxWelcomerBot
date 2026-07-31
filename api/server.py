"""
API de la mini-application Ziox.
Sert de pont entre la webapp (webapp/index.html) et la base de données partagée
avec le bot Telegram.

Sécurité : chaque requête doit fournir le "initData" transmis par Telegram.WebApp
en en-tête HTTP `X-Telegram-Init-Data`. Ce champ est vérifié via HMAC-SHA256 avec
le token du bot, comme recommandé par la documentation officielle Telegram, pour
s'assurer qu'une requête vient bien de l'utilisateur Telegram qu'elle prétend être.
"""

import os
import sys
import time
import hmac
import hashlib
import random
from urllib.parse import parse_qsl

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bot"))
from database import (  # noqa: E402
    SessionLocal, init_db, User, CompteBancaire, Transaction, Famille,
    InvitationFamille, Coffre, ObjetInventaire, ActifBoursier, Position,
    get_or_create_user,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DELAI_COFFRE_SECONDES = 5 * 60  # 5 minutes

app = Flask(__name__)
CORS(app)

init_db()


# ----------------------------------------------------------------------
# VÉRIFICATION DES DONNÉES TELEGRAM (sécurité)
# ----------------------------------------------------------------------

class SimpleUser:
    """Objet minimal compatible avec get_or_create_user() côté API."""
    def __init__(self, id, username, first_name, last_name=None):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name


def verifier_init_data(init_data: str):
    """Vérifie la signature Telegram et renvoie les infos utilisateur si valide."""
    if not init_data:
        return None
    try:
        paires = dict(parse_qsl(init_data, strict_parsing=True))
        hash_recu = paires.pop("hash", None)
        chaine_verif = "\n".join(f"{k}={v}" for k, v in sorted(paires.items()))
        cle_secrete = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        hash_calcule = hmac.new(cle_secrete, chaine_verif.encode(), hashlib.sha256).hexdigest()
        if hash_calcule != hash_recu:
            return None

        import json
        user_json = json.loads(paires.get("user", "{}"))
        return SimpleUser(
            id=user_json.get("id"),
            username=user_json.get("username"),
            first_name=user_json.get("first_name", "Joueur"),
            last_name=user_json.get("last_name"),
        )
    except Exception:
        return None


def utilisateur_courant():
    """En mode développement (pas de token configuré), autorise un user_id passé en query."""
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    tg_user = verifier_init_data(init_data)
    if tg_user:
        return tg_user

    if not BOT_TOKEN:  # mode dev sans token : on fait confiance au paramètre user_id
        uid = request.args.get("user_id") or (request.json or {}).get("user_id")
        if uid:
            return SimpleUser(id=int(uid), username=None, first_name="Testeur")
    return None


def erreur_auth():
    return jsonify({"erreur": "Authentification Telegram invalide."}), 401


# ----------------------------------------------------------------------
# PROFIL
# ----------------------------------------------------------------------

@app.route("/api/profil", methods=["GET"])
def get_profil():
    tg_user = utilisateur_courant()
    if not tg_user:
        return erreur_auth()

    session = SessionLocal()
    try:
        user = get_or_create_user(session, tg_user)
        compte = session.get(CompteBancaire, user.id)
        return jsonify({
            "id": user.id,
            "nom_affiche": user.nom_affiche,
            "nationalite": user.nationalite,
            "age": user.age,
            "sexe": user.sexe,
            "diplome": user.diplome,
            "statut_relationnel": user.statut_relationnel,
            "profil_complet": user.profil_complet,
            "solde": compte.solde,
            "numero_compte": compte.numero_compte,
            "famille_id": user.famille_id,
        })
    finally:
        session.close()


@app.route("/api/profil", methods=["POST"])
def maj_profil():
    tg_user = utilisateur_courant()
    if not tg_user:
        return erreur_auth()

    data = request.json or {}
    session = SessionLocal()
    try:
        user = get_or_create_user(session, tg_user)
        user.nom_affiche = data.get("nom_affiche", user.nom_affiche)
        user.nationalite = data.get("nationalite", user.nationalite)
        user.age = data.get("age", user.age)
        user.sexe = data.get("sexe", user.sexe)
        user.diplome = data.get("diplome", user.diplome)
        user.statut_relationnel = data.get("statut_relationnel", user.statut_relationnel)
        user.profil_complet = True
        session.commit()
        return jsonify({"ok": True})
    finally:
        session.close()


# ----------------------------------------------------------------------
# BANQUE
# ----------------------------------------------------------------------

@app.route("/api/banque/virement", methods=["POST"])
def virement():
    tg_user = utilisateur_courant()
    if not tg_user:
        return erreur_auth()

    data = request.json or {}
    destinataire_id = data.get("destinataire_id")
    montant = float(data.get("montant", 0))

    if montant <= 0:
        return jsonify({"erreur": "Montant invalide."}), 400

    session = SessionLocal()
    try:
        expediteur = get_or_create_user(session, tg_user)
        compte_exp = session.get(CompteBancaire, expediteur.id)
        compte_dest = session.get(CompteBancaire, destinataire_id)

        if not compte_dest:
            return jsonify({"erreur": "Destinataire introuvable."}), 404
        if compte_exp.solde < montant:
            return jsonify({"erreur": "Solde insuffisant."}), 400

        compte_exp.solde -= montant
        compte_dest.solde += montant
        session.add(Transaction(
            expediteur_id=expediteur.id, destinataire_id=destinataire_id,
            montant=montant, type="virement",
        ))
        session.commit()
        return jsonify({"ok": True, "nouveau_solde": compte_exp.solde})
    finally:
        session.close()


@app.route("/api/banque/historique", methods=["GET"])
def historique():
    tg_user = utilisateur_courant()
    if not tg_user:
        return erreur_auth()

    session = SessionLocal()
    try:
        transactions = (
            session.query(Transaction)
            .filter(
                (Transaction.expediteur_id == tg_user.id) |
                (Transaction.destinataire_id == tg_user.id)
            )
            .order_by(Transaction.date.desc())
            .limit(30)
            .all()
        )
        return jsonify([{
            "id": t.id,
            "expediteur_id": t.expediteur_id,
            "destinataire_id": t.destinataire_id,
            "montant": t.montant,
            "type": t.type,
            "date": t.date.isoformat(),
        } for t in transactions])
    finally:
        session.close()


# ----------------------------------------------------------------------
# COFFRES (toutes les 5 minutes)
# ----------------------------------------------------------------------

TABLE_BUTIN = [
    # (catégorie, nom, marque, rareté, valeur_min, valeur_max, poids)
    ("argent", "Liasse de ZCoins", None, "commun", 20, 80, 45),
    ("argent", "Coffret de ZCoins", None, "rare", 100, 250, 20),
    ("voiture", "Citadine", "Volkswagen", "commun", 500, 800, 15),
    ("voiture", "Berline", "BMW", "rare", 1500, 2500, 8),
    ("voiture", "Supercar", "Ferrari", "épique", 5000, 9000, 3),
    ("voiture", "Hypercar", "Bugatti", "légendaire", 15000, 25000, 1),
    ("objet_rare", "Montre de luxe", "Rolex", "épique", 3000, 6000, 4),
    ("objet_rare", "Œuvre d'art", None, "légendaire", 8000, 20000, 1),
]


def tirer_butin():
    poids_total = sum(item[6] for item in TABLE_BUTIN)
    tirage = random.uniform(0, poids_total)
    cumul = 0
    for item in TABLE_BUTIN:
        cumul += item[6]
        if tirage <= cumul:
            categorie, nom, marque, rarete, vmin, vmax, _ = item
            valeur = round(random.uniform(vmin, vmax), 2)
            return categorie, nom, marque, rarete, valeur
    return TABLE_BUTIN[0][:5]


@app.route("/api/coffre/etat", methods=["GET"])
def coffre_etat():
    tg_user = utilisateur_courant()
    if not tg_user:
        return erreur_auth()

    session = SessionLocal()
    try:
        get_or_create_user(session, tg_user)
        coffre = session.get(Coffre, tg_user.id)
        temps_ecoule = time.time() - (coffre.dernier_ouverture or 0)
        attente_restante = max(0, DELAI_COFFRE_SECONDES - temps_ecoule)
        return jsonify({"disponible": attente_restante == 0, "secondes_restantes": int(attente_restante)})
    finally:
        session.close()


@app.route("/api/coffre/ouvrir", methods=["POST"])
def coffre_ouvrir():
    tg_user = utilisateur_courant()
    if not tg_user:
        return erreur_auth()

    session = SessionLocal()
    try:
        user = get_or_create_user(session, tg_user)
        coffre = session.get(Coffre, user.id)
        temps_ecoule = time.time() - (coffre.dernier_ouverture or 0)

        if temps_ecoule < DELAI_COFFRE_SECONDES:
            return jsonify({
                "erreur": "Coffre pas encore prêt.",
                "secondes_restantes": int(DELAI_COFFRE_SECONDES - temps_ecoule),
            }), 400

        categorie, nom, marque, rarete, valeur = tirer_butin()
        coffre.dernier_ouverture = time.time()

        if categorie == "argent":
            compte = session.get(CompteBancaire, user.id)
            compte.solde += valeur
            session.add(Transaction(destinataire_id=user.id, montant=valeur, type="coffre", note=nom))
        else:
            session.add(ObjetInventaire(
                user_id=user.id, categorie=categorie, nom=nom,
                marque=marque, rarete=rarete, valeur=valeur,
            ))

        session.commit()
        return jsonify({
            "categorie": categorie, "nom": nom, "marque": marque,
            "rarete": rarete, "valeur": valeur,
        })
    finally:
        session.close()


@app.route("/api/inventaire", methods=["GET"])
def inventaire():
    tg_user = utilisateur_courant()
    if not tg_user:
        return erreur_auth()

    session = SessionLocal()
    try:
        objets = session.query(ObjetInventaire).filter_by(user_id=tg_user.id).all()
        return jsonify([{
            "id": o.id, "categorie": o.categorie, "nom": o.nom,
            "marque": o.marque, "rarete": o.rarete, "valeur": o.valeur,
        } for o in objets])
    finally:
        session.close()


# ----------------------------------------------------------------------
# FAMILLE
# ----------------------------------------------------------------------

@app.route("/api/famille", methods=["GET"])
def famille_info():
    tg_user = utilisateur_courant()
    if not tg_user:
        return erreur_auth()

    session = SessionLocal()
    try:
        user = get_or_create_user(session, tg_user)
        if not user.famille_id:
            return jsonify({"famille": None})
        famille = session.get(Famille, user.famille_id)
        membres = session.query(User).filter_by(famille_id=famille.id).all()
        return jsonify({
            "famille": {
                "id": famille.id, "nom": famille.nom,
                "solde_commun": famille.solde_commun,
                "membres": [{"id": m.id, "nom": m.nom_affiche or m.first_name} for m in membres],
            }
        })
    finally:
        session.close()


# ----------------------------------------------------------------------
# BOURSE SIMULÉE (temps réel simplifié)
# ----------------------------------------------------------------------

def actualiser_prix(actif: ActifBoursier):
    """Fait évoluer le prix selon le temps écoulé, façon marche aléatoire bornée."""
    maintenant = time.time()
    minutes_ecoulees = min(30, (maintenant - (actif.derniere_maj or maintenant)) / 60)
    if minutes_ecoulees <= 0:
        return
    variation = 1 + random.uniform(-actif.volatilite, actif.volatilite) * minutes_ecoulees
    actif.prix = max(0.5, round(actif.prix * variation, 2))
    actif.derniere_maj = maintenant


@app.route("/api/bourse", methods=["GET"])
def bourse():
    session = SessionLocal()
    try:
        actifs = session.query(ActifBoursier).all()
        for a in actifs:
            actualiser_prix(a)
        session.commit()
        return jsonify([{
            "symbole": a.symbole, "nom": a.nom, "prix": a.prix,
        } for a in actifs])
    finally:
        session.close()


@app.route("/api/bourse/ordre", methods=["POST"])
def bourse_ordre():
    tg_user = utilisateur_courant()
    if not tg_user:
        return erreur_auth()

    data = request.json or {}
    symbole = data.get("symbole")
    action = data.get("action")  # "acheter" / "vendre"
    quantite = float(data.get("quantite", 0))

    if quantite <= 0:
        return jsonify({"erreur": "Quantité invalide."}), 400

    session = SessionLocal()
    try:
        user = get_or_create_user(session, tg_user)
        compte = session.get(CompteBancaire, user.id)
        actif = session.get(ActifBoursier, symbole)
        if not actif:
            return jsonify({"erreur": "Actif inconnu."}), 404
        actualiser_prix(actif)

        position = (
            session.query(Position)
            .filter_by(user_id=user.id, symbole=symbole)
            .first()
        )
        if not position:
            position = Position(user_id=user.id, symbole=symbole, quantite=0, prix_moyen_achat=0)
            session.add(position)
            session.flush()

        cout = actif.prix * quantite

        if action == "acheter":
            if compte.solde < cout:
                return jsonify({"erreur": "Solde insuffisant."}), 400
            nouvelle_qte = position.quantite + quantite
            position.prix_moyen_achat = (
                (position.prix_moyen_achat * position.quantite) + cout
            ) / nouvelle_qte
            position.quantite = nouvelle_qte
            compte.solde -= cout
            compte.solde_investi += cout

        elif action == "vendre":
            if position.quantite < quantite:
                return jsonify({"erreur": "Quantité détenue insuffisante."}), 400
            position.quantite -= quantite
            compte.solde += cout
            compte.solde_investi = max(0, compte.solde_investi - cout)
        else:
            return jsonify({"erreur": "Action invalide."}), 400

        session.commit()
        return jsonify({"ok": True, "nouveau_solde": compte.solde, "position": position.quantite})
    finally:
        session.close()


@app.route("/api/bourse/positions", methods=["GET"])
def bourse_positions():
    tg_user = utilisateur_courant()
    if not tg_user:
        return erreur_auth()

    session = SessionLocal()
    try:
        positions = session.query(Position).filter_by(user_id=tg_user.id).filter(Position.quantite > 0).all()
        resultat = []
        for p in positions:
            actif = session.get(ActifBoursier, p.symbole)
            actualiser_prix(actif)
            resultat.append({
                "symbole": p.symbole, "nom": actif.nom, "quantite": p.quantite,
                "prix_moyen_achat": p.prix_moyen_achat, "prix_actuel": actif.prix,
                "valeur": round(p.quantite * actif.prix, 2),
                "gain_pct": round((actif.prix / p.prix_moyen_achat - 1) * 100, 2) if p.prix_moyen_achat else 0,
            })
        session.commit()
        return jsonify(resultat)
    finally:
        session.close()


@app.route("/health")
def healthcheck():
    """Endpoint de santé pour Railway / autres services."""
    return jsonify({"status": "ok"}), 200

@app.route("/")
def index():
    """Sert la mini-app webapp/index.html."""
    html_path = os.path.join(os.path.dirname(__file__), "..", "webapp", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    response = make_response(content)
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
