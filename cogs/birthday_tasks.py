"""
Module des tâches automatiques pour les anniversaires
"""

import discord
from discord import ScheduledEventLocation
from discord.ext import commands, tasks
import json
from datetime import datetime, timedelta
import os

class BirthdayTasks(commands.Cog):
    """Tâches automatiques pour les anniversaires"""
    
    def __init__(self, bot):
        self.bot = bot
        self.data_file = 'data/birthdays.json'
        
        # Chargement de la configuration
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.emojis = self.config['emojis']
        
        # Démarrage de la tâche de vérification
        self.check_birthdays.start()
    
    def cog_unload(self):
        """Arrêt de la tâche lors du déchargement du cog"""
        self.check_birthdays.cancel()
    
    def load_birthdays(self):
        """Charge les anniversaires depuis le fichier JSON"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"birthdays": {}}
    
    def get_display_name(self, guild, user_id):
        """Récupère le pseudo du serveur ou le nom d'utilisateur"""
        try:
            member = guild.get_member(int(user_id))
            if member:
                return member.display_name
            # Si le membre n'est pas trouvé, retourne le nom sauvegardé
            data = self.load_birthdays()
            if str(user_id) in data['birthdays']:
                return data['birthdays'][str(user_id)].get('username', 'Utilisateur inconnu')
            return 'Utilisateur inconnu'
        except:
            return 'Utilisateur inconnu'
    
    @tasks.loop(hours=24)
    async def check_birthdays(self):
        """Vérifie quotidiennement les anniversaires et envoie des messages"""
        
        # Attendre que le bot soit prêt
        await self.bot.wait_until_ready()
        
        today = datetime.now()
        data = self.load_birthdays()
        birthdays = data.get('birthdays', {})
        
        # Recherche des anniversaires du jour
        today_birthdays = []
        for user_id, info in birthdays.items():
            if info['day'] == today.day and info['month'] == today.month:
                today_birthdays.append({
                    'user_id': user_id,
                    'username': info['username'],
                    'year': info.get('year')
                })
        
        if not today_birthdays:
            return
        
        # Récupération du canal d'annonces
        channel_id = os.getenv('BIRTHDAY_CHANNEL_ID')
        if not channel_id:
            print("⚠️ BIRTHDAY_CHANNEL_ID non configuré dans .env")
            return
        
        channel = self.bot.get_channel(int(channel_id))
        if not channel:
            print(f"❌ Canal {channel_id} introuvable")
            return
        
        # Envoi des messages d'anniversaire
        for bday in today_birthdays:
            user = await self.bot.fetch_user(int(bday['user_id']))
            
            # Récupère le pseudo du serveur
            guild = channel.guild
            display_name = self.get_display_name(guild, bday['user_id'])
            
            # Calcul de l'âge si disponible
            age_text = ""
            if bday['year']:
                age = today.year - bday['year']
                age_text = f" qui fête ses **{age} ans**"
            
            embed = discord.Embed(
                title=f"{self.emojis['party']} Joyeux Anniversaire! {self.emojis['cake']}",
                description=f"Aujourd'hui c'est l'anniversaire de {user.mention}{age_text}!\n\n"
                           f"{self.emojis['gift']} Souhaitons-lui un excellent anniversaire! {self.emojis['balloon']}",
                color=discord.Color.from_rgb(255, 105, 180)
            )
            
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"🎊 Bon anniversaire {display_name}! 🎊")
            
            await channel.send(embed=embed)
            
            # Création d'un événement Discord (optionnel)
            await self.create_birthday_event(user, bday, guild)
    
    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        """Attend que le bot soit prêt et synchronise l'heure"""
        await self.bot.wait_until_ready()
        
        # Attendre jusqu'à l'heure configurée
        now = datetime.now()
        check_hour = int(os.getenv('CHECK_HOUR', 9))
        check_minute = int(os.getenv('CHECK_MINUTE', 0))
        
        next_run = now.replace(hour=check_hour, minute=check_minute, second=0, microsecond=0)
        
        if next_run < now:
            next_run += timedelta(days=1)
        
        wait_seconds = (next_run - now).total_seconds()
        print(f"⏰ Prochaine vérification des anniversaires dans {wait_seconds/3600:.1f}h")
        
        await discord.utils.sleep_until(next_run)
    
    async def create_birthday_event(self, user, birthday_info, guild):
        """Crée un événement Discord pour l'anniversaire (année prochaine)"""
        
        try:
            if not guild:
                guild_id = os.getenv('GUILD_ID')
                if not guild_id:
                    return
                guild = self.bot.get_guild(int(guild_id))
                if not guild:
                    return
            
            # Récupère le pseudo du serveur
            display_name = self.get_display_name(guild, birthday_info['user_id'])
            
            # Date de l'anniversaire l'année prochaine
            today = datetime.now()
            next_birthday = datetime(
                today.year + 1,
                birthday_info.get('month', today.month),
                birthday_info.get('day', today.day),
                0, 0  # 14h00
            )
            
            # Calcul de l'âge si disponible
            age_text = ""
            if birthday_info.get('year'):
                age = next_birthday.year - birthday_info['year']
                age_text = f" ({age} ans)"
            
            event_name = f"🎂 Anniversaire de {display_name}{age_text}"
            
            # Vérifier si l'événement existe déjà
            existing_events = await guild.fetch_scheduled_events()
            for event in existing_events:
                if event.name.lower() == event_name.lower():
                    print(f"ℹ️ Événement déjà existant pour {display_name}")
                    return
            
            # Création de l'événement (location est simplement une string pour external events)
            await guild.create_scheduled_event(
                name=event_name,
                description=f"Joyeux anniversaire à {display_name}! 🎉🎊🎁\n\nN'oubliez pas de lui souhaiter un bon anniversaire!",
                start_time=next_birthday,
                end_time=next_birthday.replace(hour=23, minute=59),  # Fin de journée
                location="🎈 Serveur Discord"
            )
            
            print(f"✅ Événement créé pour l'anniversaire de {display_name} (année prochaine)")
            
        except discord.Forbidden:
            print(f"❌ Permission refusée pour créer l'événement de {display_name}")
        except discord.HTTPException as e:
            print(f"❌ Erreur HTTP lors de la création de l'événement: {e}")
        except Exception as e:
            print(f"❌ Erreur lors de la création de l'événement: {e}")

def setup(bot):
    bot.add_cog(BirthdayTasks(bot))
