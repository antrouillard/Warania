# 🎂 Warania Birthday Bot

Bot Discord en Python pour gérer et afficher les anniversaires des membres du serveur.

## ✨ Fonctionnalités

- 📝 **Enregistrement des anniversaires** - Chaque membre peut enregistrer son anniversaire
- 📋 **Liste complète** - Affichage organisé par mois dans un embed stylisé
- 🔔 **Notifications automatiques** - Annonce quotidienne des anniversaires
- 📅 **Événements Discord** - Création automatique d'événements pour chaque anniversaire
- 🎯 **Prochains anniversaires** - Voir qui fête bientôt son anniversaire

## 📦 Installation

### Prérequis
- Python 3.8 ou supérieur
- Un bot Discord (créé sur [Discord Developer Portal](https://discord.com/developers/applications))

### Étapes

1. **Cloner le projet**
```bash
git clone <votre-repo>
cd Warania
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configuration**
   - Copier `.env.example` vers `.env`
   - Remplir les variables :
     - `DISCORD_TOKEN` : Token de votre bot
     - `GUILD_ID` : ID de votre serveur Discord
     - `BIRTHDAY_CHANNEL_ID` : ID du canal pour les annonces
     - `CHECK_HOUR` : Heure de vérification (défaut: 9h)

4. **Lancer le bot**
```bash
python main.py
```

## 🎮 Commandes

| Commande | Description | Permissions |
|----------|-------------|-------------|
| `/anniv_set <jour> <mois> [année]` | Enregistrer votre anniversaire | Tous |
| `/anniv_list` | Afficher tous les anniversaires (par mois) | Tous |
| `/anniv_next` | Voir les 5 prochains anniversaires | Tous |
| `/anniv_get [@membre]` | Consulter l'anniversaire d'un membre | Tous |
| `/anniv_remove [@membre]` | Supprimer un anniversaire | Admin |
| `/anniv_create_events` | 🆕 Créer des événements Discord pour tous les anniversaires | Admin |

## 📁 Structure du projet

```
warania-bot/
├── .env                      # Configuration (token, IDs)
├── .env.example             # Template de configuration
├── .gitignore              
├── requirements.txt         # Dépendances Python
├── config.json              # Configuration du bot (couleurs, emojis)
├── README.md               
├── main.py                  # Point d'entrée du bot
├── data/
│   └── birthdays.json       # Base de données des anniversaires
└── cogs/
    ├── birthday_commands.py # Commandes slash
    └── birthday_tasks.py    # Tâches automatiques
```

## 🎨 Format d'affichage

Les anniversaires sont affichés dans un **embed Discord** élégant et organisé par mois :

```
🎉 Liste des anniversaires des membres de SRBB

Janvier:
Dimitri          23/01/2003

Février:
Killian          02/02/2001
Antoine          07/02/2004
Raphael          17/02/2003

Mars:
Nohémie          13/03/2003
William          13/03/2005

[etc...]
```

## 💾 Stockage des données

Les anniversaires sont stockés dans `data/birthdays.json` :

```json
{
  "birthdays": {
    "123456789": {
      "username": "Antoine",
      "day": 7,
      "month": 2,
      "year": 2004
    }
  }
}
```

Le fichier est facilement éditable manuellement si besoin.

## 🔧 Configuration avancée

### Personnalisation des couleurs
Modifiez `config.json` pour changer les couleurs des embeds.

### Modification de l'heure de vérification
Changez `CHECK_HOUR` et `CHECK_MINUTE` dans `.env`.

### Événements Discord
Le bot crée automatiquement des événements pour les anniversaires de l'année suivante.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📝 Licence

Ce projet est sous licence MIT.

## 🎊 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.

---

Fait avec ❤️ pour la communauté KCS2 - Written by Antoine ROUILLARD
