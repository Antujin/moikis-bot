from discord.ext import commands
import discord
from Modules import PublishSheets
from Modules import Raidhelper2Sheets
from Modules.helpers import is_in_channel, WrongChannel



class ExportRaidHelper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @is_in_channel('offi-chat')
    async def ExportEvent(self, ctx, eventID):
        progress = await ctx.send(f'Export gestartet.')
        response = Raidhelper2Sheets.export_data_to_google(eventID)
        print(response)
        if response[0] == 'OK':
            await ctx.send(
                f'Anmeldungen für {response[1].strftime("%A den %d.%m.%Y")} erfolgreich exportiert. Hier der Link: {response[2]} \n Um den Kader zu veröffentlichen den folgenden Befehl ausführen: $ExportKader "{response[3]}"')
        else:
            await ctx.send('Es ist ein Fehler aufgetreten. Bitte melde dich bei <@!269164316832432128>')
        await progress.delete()

    @commands.command()
    @is_in_channel('offi-chat')
    async def ExportKader(self, ctx, sheet_name):
        progress = await ctx.send(f'Veröffentlichung gestartet.')
        response = PublishSheets.publishsheets(sheet_name)
        if response[0] == 'OK':
            channel = discord.utils.get(ctx.guild.channels, name='ankündigungen')
            mention = discord.utils.get(ctx.guild.roles, name='Mah Oida')
            await channel.send(f'{mention.mention} Hier der Kader für morgen: {response[1]}')
            await ctx.send(f'Kader in {channel.name} veröffentlicht')
        await progress.delete()

    @ExportEvent.error
    async def export_error(self, ctx, error):
        if isinstance(error, WrongChannel):
            await ctx.send(error)
