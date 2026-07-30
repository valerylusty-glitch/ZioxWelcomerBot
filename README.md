# 🏙️ Ziox Bot — Bot Telegram Welcomer + Mini-App

Une base complète, prête à personnaliser :
- 👋 Message d'accueil (privé + nouveaux membres de groupe) avec du texte soigné et des émojis
- 🎮 Menu de mini-jeux (dé, pierre-papier-ciseaux, deviner le nombre)
- 🏙️ **Ziox** : une mini-application Telegram (ville virtuelle cliquable, avec ZCoins, énergie et bâtiments à construire)
- 🔘 Boutons inline pour naviguer sans taper de commande

---

## 📁 Structure du projet

```
ziox_bot/
├── bot.py              # Le bot Telegram (Python)
├── requirements.txt    # Dépendances Python
├── .env.example         # Modèle de configuration
└── webapp/
    └── index.html       # La mini-app Ziox (à héberger en HTTPS)
```

---

## 1️⃣ Créer le bot sur Telegram

1. Ouvre une conversation avec [@BotFather](https://t.me/BotFather)
2. Envoie `/newbot` et suis les instructions
3. Récupère le **token** fourni (format `123456789:AAxxxxxxx...`)

---

## 2️⃣ Installer le projet

```bash
pip install -r requirements.txt
cp .env.example .env
```

Ouvre `.env` et remplis :

```
BOT_TOKEN=le_token_donné_par_BotFather
WEBAPP_URL=https://ton-domaine.exemple/webapp/index.html
```

> ⚠️ Telegram **exige une URL HTTPS publique** pour les mini-apps (WebApp). `localhost` ne fonctionne pas depuis l'app Telegram.

---

## 3️⃣ Héberger la mini-app Ziox

Le fichier `webapp/index.html` est autonome (HTML/CSS/JS, aucune dépendance externe à installer). Héberge-le sur un service gratuit, par exemple :

- **GitHub Pages** (glisser le dossier `webapp/` dans un repo, activer Pages)
- **Vercel** ou **Netlify** (drag & drop du dossier)
- Ton propre serveur avec certificat SSL

Une fois en ligne, copie l'URL exacte du fichier `index.html` dans `WEBAPP_URL`.

💡 Optionnel : configure aussi un **bouton de menu** dans BotFather (`/setmenubutton`) pointant vers la même URL, pour que Ziox soit accessible directement depuis l'icône ☰ du chat.

---

## 4️⃣ Lancer le bot

```bash
python bot.py
```

Le bot tourne en polling — laisse le terminal ouvert (ou déploie-le sur un serveur / Railway / Render pour qu'il tourne en continu).

---

## 🎮 Commandes disponibles

| Commande   | Effet                                    |
|------------|-------------------------------------------|
| `/start`   | Menu principal avec boutons               |
| `/jeux`    | Menu des mini-jeux                        |
| `/ziox`    | Lien direct vers la mini-app Ziox         |
| `/profil`  | Affiche les infos du profil Telegram      |
| `/help`    | Aide                                      |

---

## 🧩 Pour aller plus loin

- **Sauvegarde des données Ziox** : actuellement le score repart de zéro à chaque ouverture (état en mémoire côté navigateur). Pour une vraie persistance, branche l'API `Telegram.WebApp.CloudStorage` (native, pas besoin de backend) ou connecte la webapp à ta propre base de données via une petite API.
- **Ajouter des jeux** : duplique le schéma des fonctions `jeu_*` dans `bot.py`.
- **Habiller le message d'accueil de groupe** avec une image : utilise `reply_photo()` au lieu de `reply_text()`.
- **Statistiques multi-joueurs** : stocke `state` par utilisateur (ex. base SQLite) plutôt qu'en mémoire JS si tu veux un vrai classement entre joueurs.

Bon développement ! 🚀

