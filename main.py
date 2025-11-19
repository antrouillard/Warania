"""
Warania Birthday Bot
Bot Discord pour gérer les anniversaires des membres
"""

import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None,
    debug_guilds=[int(os.getenv('GUILD_ID'))] if os.getenv('GUILD_ID') else None  # Synchronisation rapide pour votre serveur
)

# Chargement de la configuration
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

@bot.event
async def on_ready():
    """Événement déclenché quand le bot est prêt"""
    print(f'✅ {bot.user} est connecté!')
    print(f'📊 Connecté à {len(bot.guilds)} serveur(s)')
    print(f'🔄 Commandes synchronisées automatiquement par py-cord')
    
    # Changement du statut
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="les anniversaires 🎂"
        )
    )

@bot.event
async def on_application_command_error(ctx, error):
    """Gestion des erreurs des commandes"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.respond("❌ Vous n'avez pas les permissions nécessaires.", ephemeral=True)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.respond("❌ Arguments manquants. Vérifiez la commande.", ephemeral=True)
    else:
        await ctx.respond(f"❌ Une erreur est survenue: {str(error)}", ephemeral=True)
        print(f"Erreur: {error}")

# Chargement des cogs
def load_cogs():
    """Charge tous les modules (cogs) du bot"""
    cogs_list = [
        'cogs.birthday_commands',
        'cogs.birthday_tasks'
    ]
    
    for cog in cogs_list:
        try:
            bot.load_extension(cog)
            print(f'✅ Cog chargé: {cog}')
        except Exception as e:
            print(f'❌ Erreur lors du chargement de {cog}: {e}')

if __name__ == '__main__':
    load_cogs()
    
    # Démarrage du bot
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('❌ DISCORD_TOKEN non trouvé dans le fichier .env')
        exit(1)
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        print('❌ Token invalide. Vérifiez votre DISCORD_TOKEN.')
    except Exception as e:
        print(f'❌ Erreur lors du démarrage: {e}')
