from discord.ext import commands
import discord


class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rolechannel = None
        self.guild = None

    @commands.Cog.listener()
    async def on_ready(self):
        guilds = []
        async for guild in self.bot.fetch_guilds():
            guilds.append(guild)
        self.guild = guilds[0]
        channels_on_server = await guilds[0].fetch_channels()
        self.rolechannel = discord.utils.get(channels_on_server, name='get-roles')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        payloadchannel = await self.bot.fetch_channel(payload.channel_id)
        print(payloadchannel, self.rolechannel)
        if payloadchannel == self.rolechannel:
            print(payloadchannel, payload.member, payload.emoji)