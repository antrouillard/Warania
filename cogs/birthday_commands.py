"""
Module des commandes d'anniversaires
"""

import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from discord import ScheduledEventLocation
import json
from datetime import datetime
from typing import Optional
import os

class BirthdayCommands(commands.Cog):
    """Commandes pour gérer les anniversaires"""
    
    def __init__(self, bot):
        self.bot = bot
        self.data_file = 'data/birthdays.json'
        
        # Chargement de la configuration
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.months_fr = self.config['months_fr']
        self.emojis = self.config['emojis']
    
    def load_birthdays(self):
        """Charge les anniversaires depuis le fichier JSON"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"birthdays": {}}
    
    def save_birthdays(self, data):
        """Sauvegarde les anniversaires dans le fichier JSON"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_display_name(self, guild, user_id):
        """Récupère le pseudo du serveur ou le nom d'utilisateur"""
        try:
            member = guild.get_member(int(user_id))
            if member:
                # Utilise le surnom du serveur s'il existe, sinon le display_name
                return member.display_name
            # Si le membre n'est pas trouvé, retourne le nom sauvegardé
            data = self.load_birthdays()
            if str(user_id) in data['birthdays']:
                return data['birthdays'][str(user_id)].get('username', 'Utilisateur inconnu')
            return 'Utilisateur inconnu'
        except:
            return 'Utilisateur inconnu'
    
    @slash_command(
        name="anniv_set",
        description="Enregistrer votre anniversaire"
    )
    async def set_birthday(
        self,
        ctx,
        jour: Option(int, "Jour de naissance (1-31)", min_value=1, max_value=31, required=True),
        mois: Option(int, "Mois de naissance (1-12)", min_value=1, max_value=12, required=True),
        annee: Option(int, "Année de naissance (optionnel)", min_value=1900, max_value=2020, required=False)
    ):
        """Enregistre l'anniversaire d'un utilisateur"""
        
        # Validation de la date
        try:
            if annee:
                datetime(annee, mois, jour)
            else:
                datetime(2000, mois, jour)  # Année fictive pour validation
        except ValueError:
            await ctx.respond("❌ Date invalide! Vérifiez le jour et le mois.", ephemeral=True)
            return
        
        # Chargement des données
        data = self.load_birthdays()
        user_id = str(ctx.author.id)
        
        # Enregistrement
        data['birthdays'][user_id] = {
            'username': ctx.author.name,
            'day': jour,
            'month': mois,
            'year': annee if annee else None
        }
        
        self.save_birthdays(data)
        
        # Message de confirmation
        date_str = f"{jour:02d}/{mois:02d}"
        if annee:
            date_str += f"/{annee}"
        
        embed = discord.Embed(
            title=f"{self.emojis['cake']} Anniversaire enregistré!",
            description=f"Votre anniversaire a été enregistré pour le **{date_str}**",
            color=discord.Color.from_rgb(255, 105, 180)
        )
        
        await ctx.respond(embed=embed, ephemeral=True)
    
    @slash_command(
        name="anniv_list",
        description="Afficher la liste de tous les anniversaires"
    )
    async def list_birthdays(self, ctx):
        """Affiche tous les anniversaires organisés par mois"""
        
        data = self.load_birthdays()
        birthdays = data.get('birthdays', {})
        
        if not birthdays:
            await ctx.respond("📭 Aucun anniversaire enregistré pour le moment.", ephemeral=True)
            return
        
        # Organisation par mois
        by_month = {}
        for user_id, info in birthdays.items():
            month = info['month']
            if month not in by_month:
                by_month[month] = []
            by_month[month].append(info)
        
        # Tri des anniversaires dans chaque mois
        for month in by_month:
            by_month[month].sort(key=lambda x: x['day'])
        
        # Création de l'embed
        embed = discord.Embed(
            title=f"{self.emojis['party']} Liste des anniversaires des membres du KCS2",
            color=discord.Color.from_rgb(255, 105, 180)
        )
        
        # Ajout d'une image/icône (optionnel)
        embed.set_thumbnail(url="https://em-content.zobj.net/source/twitter/376/birthday-cake_1f382.png")
        
        # Ajout des mois dans l'ordre
        for month in sorted(by_month.keys()):
            month_name = self.months_fr[str(month)]
            
            # Formatage des anniversaires du mois
            birthdays_text = ""
            for bday in by_month[month]:
                # Récupère le pseudo du serveur pour chaque membre
                user_id = None
                for uid, info in birthdays.items():
                    if info == bday:
                        user_id = uid
                        break
                
                name = self.get_display_name(ctx.guild, user_id) if user_id else bday['username']
                day = bday['day']
                year = bday.get('year', '')
                date_str = f"{day:02d}/{month:02d}/{year}" if year else f"{day:02d}/{month:02d}"
                
                # Espacement pour alignement
                birthdays_text += f"`{name:<15} {date_str}`\n"
            
            embed.add_field(
                name=f"**{month_name}:**",
                value=birthdays_text if birthdays_text else "Aucun",
                inline=False
            )
        
        await ctx.respond(embed=embed)
    
    @slash_command(
        name="anniv_soon",
        description="Afficher les prochains anniversaires"
    )
    async def next_birthdays(self, ctx):
        """Affiche les prochains anniversaires à venir"""
        
        data = self.load_birthdays()
        birthdays = data.get('birthdays', {})
        
        if not birthdays:
            await ctx.respond("📭 Aucun anniversaire enregistré.", ephemeral=True)
            return
        
        today = datetime.now()
        upcoming = []
        
        for user_id, info in birthdays.items():
            # Calcul du prochain anniversaire
            bday_this_year = datetime(today.year, info['month'], info['day'])
            
            if bday_this_year < today:
                # Si déjà passé cette année, prendre l'année prochaine
                bday_next = datetime(today.year + 1, info['month'], info['day'])
            else:
                bday_next = bday_this_year
            
            days_until = (bday_next - today).days
            
            upcoming.append({
                'username': self.get_display_name(ctx.guild, user_id),
                'date': bday_next,
                'days': days_until,
                'day': info['day'],
                'month': info['month']
            })
        
        # Tri par date
        upcoming.sort(key=lambda x: x['days'])
        
        # Affichage des 5 prochains
        embed = discord.Embed(
            title=f"{self.emojis['balloon']} Prochains anniversaires",
            color=discord.Color.from_rgb(52, 152, 219)
        )
        
        for i, bday in enumerate(upcoming[:5]):
            days_text = "Aujourd'hui! 🎉" if bday['days'] == 0 else f"Dans {bday['days']} jour(s)"
            date_str = f"{bday['day']:02d}/{bday['month']:02d}"
            
            embed.add_field(
                name=f"{i+1}. {bday['username']}",
                value=f"📅 {date_str} - {days_text}",
                inline=False
            )
        
        await ctx.respond(embed=embed)
    
    @slash_command(
        name="anniv_get",
        description="Voir l'anniversaire d'un membre"
    )
    async def get_birthday(
        self,
        ctx,
        membre: Option(discord.Member, "Membre à consulter", required=False)
    ):
        """Affiche l'anniversaire d'un membre spécifique"""
        
        target = membre if membre else ctx.author
        data = self.load_birthdays()
        
        user_id = str(target.id)
        if user_id not in data['birthdays']:
            await ctx.respond(
                f"❌ Aucun anniversaire enregistré pour {target.mention}",
                ephemeral=True
            )
            return
        
        info = data['birthdays'][user_id]
        date_str = f"{info['day']:02d}/{info['month']:02d}"
        if info.get('year'):
            date_str += f"/{info['year']}"
            age = datetime.now().year - info['year']
            age_text = f"\n🎂 Âge: {age} ans"
        else:
            age_text = ""
        
        embed = discord.Embed(
            title=f"{self.emojis['cake']} Anniversaire de {target.name}",
            description=f"📅 Date: **{date_str}**{age_text}",
            color=discord.Color.from_rgb(255, 105, 180)
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        
        await ctx.respond(embed=embed)
    
    @slash_command(
        name="anniv_remove",
        description="Supprimer un anniversaire (Admin uniquement)"
    )
    @commands.has_permissions(administrator=True)
    async def remove_birthday(
        self,
        ctx,
        membre: Option(discord.Member, "Membre dont supprimer l'anniversaire", required=True)
    ):
        """Supprime l'anniversaire d'un membre (admin uniquement)"""
        
        # Vérification supplémentaire des permissions
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(
                "❌ Vous devez être administrateur pour utiliser cette commande.",
                ephemeral=True
            )
            return
        
        data = self.load_birthdays()
        user_id = str(membre.id)
        
        if user_id not in data['birthdays']:
            await ctx.respond(
                f"❌ {membre.mention} n'a pas d'anniversaire enregistré.",
                ephemeral=True
            )
            return
        
        del data['birthdays'][user_id]
        self.save_birthdays(data)
        
        await ctx.respond(
            f"✅ Anniversaire de {membre.mention} supprimé.",
            ephemeral=True
        )
    
    @slash_command(
        name="anniv_create_events",
        description="Créer des événements Discord pour tous les anniversaires à venir"
    )
    @commands.has_permissions(administrator=True)
    async def create_events(self, ctx):
        """Crée des événements Discord pour tous les anniversaires de l'année à venir"""
        
        # Vérification supplémentaire des permissions
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(
                "❌ Vous devez être administrateur pour utiliser cette commande.",
                ephemeral=True
            )
            return
        
        await ctx.defer()  # Indique que le traitement peut prendre du temps
        
        data = self.load_birthdays()
        birthdays = data.get('birthdays', {})
        
        if not birthdays:
            await ctx.respond("📭 Aucun anniversaire enregistré.", ephemeral=True)
            return
        
        guild = ctx.guild
        if not guild:
            await ctx.respond("❌ Cette commande doit être utilisée sur un serveur.", ephemeral=True)
            return
        
        today = datetime.now()
        events_created = 0
        events_failed = 0
        errors = []
        
        # Récupération des événements existants pour éviter les doublons
        existing_events = await guild.fetch_scheduled_events()
        existing_event_names = [event.name.lower() for event in existing_events]
        
        for user_id, info in birthdays.items():
            try:
                # Calcul de la date du prochain anniversaire
                bday_this_year = datetime(today.year, info['month'], info['day'], 0, 0)  # 14h00
                
                if bday_this_year < today:
                    # Si déjà passé cette année, créer pour l'année prochaine
                    bday_date = datetime(today.year + 1, info['month'], info['day'], 0, 0)
                else:
                    bday_date = bday_this_year
                
                # Récupère le pseudo du serveur
                display_name = self.get_display_name(guild, user_id)
                
                # Calcul de l'âge si disponible
                age_text = ""
                if info.get('year'):
                    age = bday_date.year - info['year']
                    age_text = f" ({age} ans)"
                
                event_name = f"🎂 Anniversaire de {display_name}{age_text}"
                
                # Vérifier si l'événement existe déjà
                if event_name.lower() in existing_event_names:
                    continue
                
                # Création de l'événement (location est simplement une string pour external events)
                event = await guild.create_scheduled_event(
                    name=event_name,
                    description=f"Joyeux anniversaire à {display_name}! 🎉🎊🎁\n\nN'oubliez pas de lui souhaiter un bon anniversaire!",
                    start_time=bday_date,
                    end_time=bday_date.replace(hour=23, minute=59),  # Fin de journée
                    location="🎈 Serveur Discord"
                )
                
                events_created += 1
                
            except discord.Forbidden:
                events_failed += 1
                display_name = self.get_display_name(guild, user_id)
                errors.append(f"Permission refusée pour {display_name}")
            except discord.HTTPException as e:
                events_failed += 1
                display_name = self.get_display_name(guild, user_id)
                errors.append(f"Erreur pour {display_name}: {str(e)}")
            except Exception as e:
                events_failed += 1
                display_name = self.get_display_name(guild, user_id)
                errors.append(f"Erreur inattendue pour {display_name}: {str(e)}")
        
        # Message de résultat
        embed = discord.Embed(
            title=f"{self.emojis['party']} Création d'événements terminée",
            color=discord.Color.from_rgb(52, 152, 219)
        )
        
        embed.add_field(
            name="✅ Événements créés",
            value=f"**{events_created}** événement(s)",
            inline=True
        )
        
        if events_failed > 0:
            embed.add_field(
                name="❌ Échecs",
                value=f"**{events_failed}** événement(s)",
                inline=True
            )
            
            if errors:
                error_text = "\n".join(errors[:5])  # Limiter à 5 erreurs
                if len(errors) > 5:
                    error_text += f"\n... et {len(errors) - 5} autre(s) erreur(s)"
                embed.add_field(
                    name="Détails des erreurs",
                    value=error_text,
                    inline=False
                )
        
        embed.set_footer(text="💡 Les événements sont créés pour les anniversaires à venir dans l'année")
        
        await ctx.followup.send(embed=embed)
    
    @slash_command(
        name="anniv_delete_events",
        description="[ADMIN] Supprimer tous les événements d'anniversaires du serveur"
    )
    async def delete_events(self, ctx):
        """Supprime tous les événements d'anniversaires (admin uniquement)"""
        
        # Vérification des permissions d'administrateur
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(
                "❌ Vous devez être administrateur pour utiliser cette commande.",
                ephemeral=True
            )
            return
        
        await ctx.defer()
        
        guild = ctx.guild
        if not guild:
            await ctx.followup.send("❌ Cette commande doit être utilisée sur un serveur.")
            return
        
        try:
            # Récupération de tous les événements du serveur
            existing_events = await guild.fetch_scheduled_events()
            
            # Filtrer uniquement les événements d'anniversaires (qui commencent par 🎂)
            birthday_events = [event for event in existing_events if event.name.startswith("🎂")]
            
            if not birthday_events:
                await ctx.followup.send("📭 Aucun événement d'anniversaire trouvé sur le serveur.")
                return
            
            # Compteurs
            deleted_count = 0
            failed_count = 0
            errors = []
            
            # Suppression des événements
            for event in birthday_events:
                try:
                    await event.delete()
                    deleted_count += 1
                except discord.Forbidden:
                    failed_count += 1
                    errors.append(f"Permission refusée pour '{event.name}'")
                except discord.HTTPException as e:
                    failed_count += 1
                    errors.append(f"Erreur pour '{event.name}': {str(e)}")
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Erreur inattendue pour '{event.name}': {str(e)}")
            
            # Message de résultat
            embed = discord.Embed(
                title=f"🗑️ Suppression d'événements terminée",
                color=discord.Color.from_rgb(231, 76, 60) if failed_count > 0 else discord.Color.from_rgb(46, 204, 113)
            )
            
            embed.add_field(
                name="✅ Événements supprimés",
                value=f"**{deleted_count}** événement(s)",
                inline=True
            )
            
            if failed_count > 0:
                embed.add_field(
                    name="❌ Échecs",
                    value=f"**{failed_count}** événement(s)",
                    inline=True
                )
                
                if errors:
                    error_text = "\n".join(errors[:5])  # Limiter à 5 erreurs
                    if len(errors) > 5:
                        error_text += f"\n... et {len(errors) - 5} autre(s) erreur(s)"
                    embed.add_field(
                        name="Détails des erreurs",
                        value=error_text,
                        inline=False
                    )
            
            embed.set_footer(text="💡 Seuls les événements d'anniversaires (🎂) ont été supprimés")
            
            await ctx.followup.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.followup.send("❌ Le bot n'a pas la permission de gérer les événements sur ce serveur.")
        except Exception as e:
            await ctx.followup.send(f"❌ Une erreur est survenue : {str(e)}")

def setup(bot):
    bot.add_cog(BirthdayCommands(bot))
