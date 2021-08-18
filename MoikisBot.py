import locale
import logging
import os


import discord
from discord.ext import commands

from Modules.ExportRaidHelper import ExportRaidHelper
from Modules.channelmanager import ChannelManager
from Modules.feedback import Feedback
from Modules.RoleManagement import RoleManager
from Modules.Voting import Voting

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter((logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')))
logger.addHandler(handler)

locale.setlocale(locale.LC_TIME, "de_DE.utf8")

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

bot.add_cog(ExportRaidHelper(bot))
bot.add_cog(Feedback(bot))
bot.add_cog(ChannelManager(bot))
bot.add_cog(RoleManager(bot))
bot.add_cog(Voting(bot))

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
if DISCORD_TOKEN == None:
    raise RuntimeError('No Discord API token found. Please set your Discord API Token as the enviroment variable "DISCORD_TOKEN"')
bot.run(DISCORD_TOKEN)

