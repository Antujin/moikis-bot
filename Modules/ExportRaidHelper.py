from discord.ext import commands
import discord
from Modules import PublishSheets
from Modules import Raidhelper2Sheets
from Modules import RaidhelperStrawpolls
from Modules.helpers import is_in_channel, WrongChannel
import datetime



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
            await progress.delete()

        else:
            await ctx.send('Es ist ein Fehler aufgetreten. Bitte melde dich bei <@!269164316832432128>')

    @commands.command()
    @is_in_channel('offi-chat')
    async def ExportKader(self, ctx, sheet_name):
        progress = await ctx.send(f'Veröffentlichung gestartet.')
        response = PublishSheets.publishsheets(sheet_name)
        if response[0] == 'OK':
            channel = discord.utils.get(ctx.guild.channels, name='kader')
            mention = discord.utils.get(ctx.guild.roles, name='Mah Oida')
            await channel.send(f'{mention.mention} Hier der Kader für morgen: {response[1]}')
            await ctx.send(f'Kader in {channel.name} veröffentlicht')
        await progress.delete()

    @commands.command()
    @is_in_channel('offi-chat')
    async def EvalPoll(self, ctx, poll_id):
        question, answers, total_responses = RaidhelperStrawpolls.read_data_from_api(poll_id)
        embed = discord.Embed(title=f'Strawpoll Ergebnisse bei {total_responses} Abstimmenden',
                              description=question,
                              color=0x0000ff)
        for answer in answers.keys():
            embed.add_field(name=f' {answers[answer]["text"]}: {answers[answer]["count"]} Stimmmen ({round(answers[answer]["count"]/total_responses*100,2)}%)',
                            value='\n'.join(answers[answer]['voters']), inline=True)

        await ctx.send(f"Ausgewertet am {datetime.datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')}", embed=embed)


    @ExportEvent.error
    async def export_error(self, ctx, error):
        if isinstance(error, WrongChannel):
            await ctx.send(error)
