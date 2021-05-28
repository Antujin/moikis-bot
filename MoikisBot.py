import locale
import logging
import os
import datetime

import discord
from discord.ext import tasks, commands

from Modules.ExportRaidHelper import ExportRaidHelper
from Modules.channelmanager import ChannelManager

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter((logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')))
logger.addHandler(handler)

locale.setlocale(locale.LC_TIME, "de_DE.utf8")



class Sonstiges(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        output_channel = discord.utils.get(bot.guilds[0].channels, name='offi-chat')
        if message.author == self.bot.user:
            return
        if message.channel.type == discord.ChannelType.private:
            mention = discord.utils.get(self.bot.guilds[0].roles, name='Mega Oida')
            embed = discord.Embed(title='Feedback', description=f'Erhalten am {datetime.datetime.now().strftime("%d.%m.%Y um %H:%M Uhr")}', color=0x00ff00)
            embed.add_field(name='Nachricht:', value=message.content, inline=False)
            await output_channel.send(f'{mention.mention}', embed=embed)
            await message.channel.send('Hallo, \nNachricht erhalten und and die Offis weitergeleitet. Du wirst keine direkte Antwort auf dein Feedback erhalten, da deine Nachricht anonymisiert wurde.')
            return

    @commands.command()
    async def test(self, ctx, arg=None):
        working_messing = await ctx.send(f'test gestartet.')
        await ctx.message.delete()
        await ctx.send(
            f'Hallo {ctx.author.name}, du hast im Channel {ctx.channel.name} den Parameter "{arg}" übergeben.',
            delete_after=60)
        await working_messing.delete()

    @test.error
    async def export_error(self, ctx, error):
        if isinstance(error, WrongChannel):
            await ctx.send(error)



bot = commands.Bot(command_prefix='$')
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

bot.add_cog(ExportRaidHelper(bot))
bot.add_cog(Sonstiges(bot))
bot.add_cog(ChannelManager(bot))

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
if DISCORD_TOKEN == None:
    raise RuntimeError('No Discord API token found. Please set your Discord API Token as the enviroment variable "DISCORD_TOKEN"')
bot.run(DISCORD_TOKEN)

