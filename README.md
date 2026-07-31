# 🏙️ Ziox — Bot Telegram professionnel + Life City

Un bot Telegram complet avec modération, accueil/au revoir personnalisables,
système familial, et une mini-application "Life City" (profil, banque virtuelle,
coffres, bourse simulée).

⚠️ **Important — lire avant de commencer :** toute l'économie du jeu (ZCoins, banque,
bourse) est **entièrement virtuelle et fictive**. Ce projet ne traite aucun vrai
paiement, aucune vraie carte bancaire, et ne connecte aucun marché financier réel —
ce serait un système financier réglementé, hors de portée d'un simple bot. La
"bourse en temps réel" est une simulation dont les prix évoluent tout seuls.

---

## 📁 Structure du projet

```
ziox_pro/
├── bot/
│   ├── main.py            # Point d'entrée du bot (commandes générales)
│   ├── database.py        # Modèles de base de données (partagés avec l'API)
│   ├── moderation.py      # kick / ban / unban / mute / unmute / warn / unwarn
│   ├── welcome.py         # Accueil / au revoir personnalisables (texte + audio)
│   ├── family.py          # Système de famille virtuelle
│   └── requirements.txt
├── api/
│   ├── server.py           # API Flask pour la mini-app (profil, banque, coffres, bourse)
│   └── requirements.txt
├── webapp/
│   └── index.html          # Mini-application Ziox (front-end)
└── env.example.txt         # Modèle de configuration
```

Le bot et l'API **partagent la même base de données** (fichier `ziox.db` par défaut),
donc les infos vues dans le chat (`/profil`, `/solde`) et dans la mini-app sont
toujours synchronisées.

---

## 1️⃣ Créer le bot

1. Ouvre [@BotFather](https://t.me/BotFather) sur Telegram
2. `/newbot` → suis les instructions → récupère le **token**
3. Active les mini-apps : `/mybots` → ton bot → `Bot Settings` → `Menu Button` →
   configure l'URL de ta webapp (voir étape 4)

---

## 2️⃣ Configuration

À la racine du projet (`ziox_pro/`) :

```bash
cp env.example.txt .env
```

Remplis `.env` :
```
BOT_TOKEN=le_token_donné_par_BotFather
WEBAPP_URL=https://ton-domaine.exemple/webapp/index.html
DATABASE_URL=sqlite:///ziox.db
PORT=5000
```

---

## 3️⃣ Installer et lancer le bot

```bash
cd bot
pip install -r requirements.txt
python main.py
```

---

## 4️⃣ Installer et lancer l'API de la mini-app

```bash
cd api
pip install -r requirements.txt
python server.py
```

L'API doit être accessible en **HTTPS public** pour que la mini-app puisse la
contacter depuis Telegram (utilise par exemple Render, Railway, Fly.io, ou un
VPS avec un reverse proxy + certificat SSL — `ngrok` fonctionne aussi pour tester).

---

## 5️⃣ Héberger et connecter la mini-app

1. Héberge `webapp/index.html` en HTTPS (GitHub Pages, Vercel, Netlify…)
2. Dans `webapp/index.html`, remplace la ligne :
   ```js
   const API_BASE = window.ZIOX_API_BASE || "https://ton-api.exemple.com";
   ```
   par l'URL réelle de ton API (étape 4).
3. Renseigne cette même URL dans `.env` → `WEBAPP_URL`, et dans le bouton de menu
   BotFather (étape 1).

---

## 🎮 Commandes du bot

### Général
| Commande | Effet |
|---|---|
| `/start` | Menu principal |
| `/profil` | Voir son profil Ziox |
| `/solde` | Voir son solde bancaire |

### Famille
| Commande | Effet |
|---|---|
| `/famille creer <nom>` | Fonder une famille |
| `/famille inviter` | Inviter (en réponse à un message) |
| `/famille accepter` | Accepter une invitation |
| `/famille quitter` | Quitter sa famille |

### Accueil / au revoir (admins)
| Commande | Effet |
|---|---|
| `/accueil on \| off` | Activer / désactiver |
| `/accueil texte <message>` | Personnaliser (variables `{prenom}` `{groupe}`) |
| `/accueil audio` | Répondre à un vocal pour le définir |
| `/accueil test` | Prévisualiser |
| `/aurevoir …` | Mêmes options pour le message de départ |

### Jeux (avec de vraies ZCoins)
| Commande | Effet |
|---|---|
| `/machine <mise>` | 🎰 Machine à sous solo — mise minimale 5 ZCoins, jackpot x25 sur triple 7️⃣ |
| `/duel <mise>` | ⚔️ Duel Pierre-Papier-Ciseaux avec mise, à faire en réponse au message de l'adversaire. Il accepte via bouton, les deux choisissent en secret, le gagnant remporte la mise du perdant. |

### Modération (admins)
| Commande | Effet |
|---|---|
| `/kick` | Expulser (répondre au message) |
| `/ban` / `/unban <id>` | Bannir / débannir |
| `/mute [minutes]` / `/unmute` | Museler / démuseler |
| `/warn <raison>` / `/unwarn` / `/warns` | Avertir (ban auto au 3ᵉ) |

---

## 🎁 Fonctionnement du jeu (mini-app)

- **Profil** : nom, nationalité, âge, sexe, diplôme, statut relationnel — à
  remplir une fois à la première ouverture.
- **Banque** : compte avec numéro unique, solde en ZCoins, virements entre
  joueurs (par ID Telegram), historique des transactions.
- **Coffres** : un coffre gratuit toutes les 5 minutes, avec table de butin
  pondérée (argent, voitures de marques fictives associées à un nom réel de
  constructeur pour l'ambiance, objets rares) — raretés commun → légendaire.
- **Bourse simulée** : 5 actifs fictifs dont le prix évolue selon une marche
  aléatoire pondérée par le temps écoulé ; achat/vente en ZCoins, suivi des
  gains/pertes en %.
- **Famille** : fondée et gérée depuis le chat (`/famille`), consultable dans
  la mini-app (solde commun, liste des membres).

---

## 🧩 Pistes pour la suite

- **Comptes joints familiaux** : ajouter un endpoint `/api/famille/deposer`
  pour alimenter le `solde_commun` depuis le solde personnel.
- **Anti-spam / anti-flood** : ajouter un `MessageHandler` qui compte les
  messages par utilisateur/minute et mute automatiquement en cas d'excès.
- **Notifications de marché** : tâche planifiée (`JobQueue` de
  python-telegram-bot) qui alerte les joueurs en cas de forte variation de prix.
- **Classement** : endpoint `/api/classement` trié par solde total (banque +
  inventaire) pour un leaderboard dans la mini-app.
- **Production** : remplacer SQLite par PostgreSQL (juste changer
  `DATABASE_URL`), et déployer bot + API sur un service persistant (Railway,
  Render, VPS) plutôt qu'en local.

Bon développement ! 🚀
