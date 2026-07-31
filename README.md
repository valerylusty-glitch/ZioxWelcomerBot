# Ziox Welcomer Bot

Bot Telegram tout-en-un avec message d'accueil/au revoir, modération, système familial, mini-jeux et mini-app.

---

## Structure du projet

```
ZioxWelcomerBot/
├── bot/
│   ├── main.py          # Point d'entrée du bot (commandes générales)
│   ├── database.py      # Modèles de base de données (partagés avec l'API)
│   ├── moderation.py    # Kick / ban / unban / mute / unmute / warn / unwarn
│   ├── welcome.py       # Accueil / au revoir personnalisables (texte + audio)
│   ├── family.py        # Système de famille virtuelle (créer, inviter, accepter, quitter)
│   └── games.py         # Machine à sous et duel Pierre-Papier-Ciseaux
├── api/
│   └── server.py        # API Flask pour la mini-app (profil, banque, coffres, bourse)
├── webapp/
│   └── index.html       # Mini-application Ziox (front-end)
├── requirements.txt     # Dépendances Python (bot + API)
├── Dockerfile           # Déploiement Railway
├── railway.json         # Configuration Railway
└── env.example.txt      # Modèle de configuration
```

---

## Fonctionnalités

### Bot Telegram

| Catégorie | Commandes | Description |
|-----------|-----------|-------------|
| Général | `/start`, `/help`, `/profil`, `/solde` | Menu principal, aide, profil, solde bancaire |
| Famille | `/famille creer`, `/famille inviter`, `/famille accepter`, `/famille quitter` | Créer et gérer une famille virtuelle |
| Jeux | `/machine <mise>`, `/duel <mise>` | Machine à sous (solo) et duel Pierre-Papier-Ciseaux |
| Accueil | `/accueil on/off/texte/audio/test` | Configurer le message de bienvenue par groupe |
| Au revoir | `/aurevoir on/off/texte/audio/test` | Configurer le message de départ par groupe |
| Modération | `/kick`, `/ban`, `/unban`, `/mute`, `/unmute`, `/warn`, `/unwarn`, `/warns` | Outils d'administration pour les admins du groupe |

### Mini-app (webapp)

La mini-app Telegram (`webapp/index.html`) connectée à l'API (`api/server.py`) propose :

- **Profil** : nationalité, âge, sexe, diplôme, statut relationnel
- **Banque** : compte avec numéro unique, solde en ZCoins, virements entre joueurs
- **Coffres** : un coffre gratuit toutes les 5 minutes avec table de butin pondérée
- **Bourse simulée** : 5 actifs fictifs dont le prix évolue, achat/vente en ZCoins
- **Famille** : solde commun et liste des membres

---

## Installation

### 1. Créer le bot Telegram

1. Ouvre [@BotFather](https://t.me/BotFather) sur Telegram
2. `/newbot` → suis les instructions → récupère le **token**
3. Active les mini-apps : `/mybots` → ton bot → `Bot Settings` → `Menu Button` → configure l'URL de ta webapp

### 2. Configuration

```bash
cp env.example.txt .env
```

Remplis `.env` :

```env
BOT_TOKEN=le_token_donné_par_BotFather
WEBAPP_URL=https://ton-domaine.exemple/webapp/index.html
DATABASE_URL=sqlite:///ziox.db
PORT=8080
```

### 3. Installer et lancer le bot

```bash
pip install -r requirements.txt
cd bot
python main.py
```

### 4. Installer et lancer l'API de la mini-app

```bash
python api/server.py
```

L'API doit être accessible en **HTTPS public** pour que la mini-app puisse la contacter depuis Telegram. Tu peux utiliser Railway, Render, Fly.io, ou un VPS avec un reverse proxy + certificat SSL.

### 5. Héberger et connecter la mini-app

1. Héberge `webapp/index.html` en HTTPS (GitHub Pages, Vercel, Netlify…)
2. Dans `webapp/index.html`, remplace la ligne :
   ```js
   const API_BASE = window.ZIOX_API_BASE || "https://ton-api.exemple.com";
   ```
   par l'URL réelle de ton API.
3. Renseigne cette même URL dans `.env` → `WEBAPP_URL`, et dans le bouton de menu BotFather.

---

## Déploiement sur Railway

Le projet est prêt pour Railway grâce au `Dockerfile` et au `railway.json` :

1. Connecte ton repo GitHub à Railway
2. Railway détecte automatiquement le `Dockerfile` et le `railway.json`
3. Ajoute les variables d'environnement dans Railway :
   - `BOT_TOKEN` — token du bot Telegram
   - `WEBAPP_URL` — URL HTTPS de la mini-app
   - `DATABASE_URL` — ex: `postgresql://user:pass@host/db` ou `sqlite:///ziox.db`
4. Le déploiement se lance automatiquement

> **Note** : Pour la production, il est recommandé de remplacer SQLite par PostgreSQL (change simplement la variable `DATABASE_URL`).

---

## Économie virtuelle

> **Important** : toute l'économie du jeu (ZCoins, banque, bourse) est **entièrement virtuelle et fictive**. Ce projet ne traite aucun vrai paiement, aucune vraie carte bancaire, et ne connecte aucun marché financier réel. La "bourse en temps réel" est une simulation dont les prix évoluent de manière aléatoire.

---

## Pistes d'amélioration

- **Comptes joints familiaux** : ajouter un endpoint `/api/famille/deposer` pour alimenter le `solde_commun` depuis le solde personnel
- **Anti-spam / anti-flood** : ajouter un handler qui compte les messages par utilisateur/minute et mute automatiquement en cas d'excès
- **Notifications de marché** : tâche planifiée (`JobQueue`) qui alerte les joueurs en cas de forte variation de prix
- **Classement** : endpoint `/api/classement` trié par solde total (banque + inventaire) pour un leaderboard dans la mini-app
