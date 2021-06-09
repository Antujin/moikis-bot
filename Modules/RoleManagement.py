from discord.ext import commands
import discord


class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rolechannel = None
        self.guild = None
        try:
            with open('raid_team.txt', 'r') as f:
                self.raid_team_message_id = f.read()
        except Exception as e:
            self.raid_team_message_id = None
            print(e)

    @commands.Cog.listener()
    async def on_ready(self):
        guilds = []
        async for guild in self.bot.fetch_guilds():
            guilds.append(guild)
        self.guild = guilds[0]
        emojis = await self.guild.fetch_emojis()
        print(emojis)
        channels_on_server = await guilds[0].fetch_channels()
        self.rolechannel = discord.utils.get(channels_on_server, name='get-roles')
        #pinned_messages = self.rolechannel.pins()
        if self.raid_team_message_id == None:
            raid_team_message = await self.rolechannel.send('Bitte wähle anhand der untenstehenden Emojis in welchem Raidteam du raiden möchtest')
            await raid_team_message.add_reaction(emoji=emojis[0])
            await raid_team_message.add_reaction(emoji=emojis[1])
            with open('raid_team.txt', 'w') as f:
                f.write(str(raid_team_message.id))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        payloadchannel = await self.bot.fetch_channel(payload.channel_id)
        if payloadchannel == self.rolechannel and not payload.member == self.bot.user:
            if payload.message_id == self.raid_team_message_id:
                if payload.emoji.id == 852162473489858580:  # Ketchup
                    print(f'{payload.member} requested the role Team Ketchup')
                elif payload.emoji.id == 852162498374139936:  # Mayo
                    print(f'{payload.member} requested the role Team Mayo')