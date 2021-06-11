from discord.ext import commands
import discord


class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rolechannel = None
        self.guild = None
        self.raid_team_message = None
        try:
            with open('raid_team.txt', 'r') as f:
                self.raid_team_message_id = int(f.read())
        except Exception as e:
            self.raid_team_message_id = None
            print(e)

    async def raid_team_role(self, payload):
        roles = await self.guild.fetch_roles()
        if payload.emoji == discord.utils.get(await self.guild.fetch_emojis(), name='ketchup'):  # Ketchup
            role = discord.utils.get(roles, name='Team Ketchup')
            if role not in payload.member.roles:
                await payload.member.add_roles(role)
                await payload.member.send(content=f'Du hast die Discord Rolle "{role}" erhalten.')
            else:
                await payload.member.remove_roles(role)
                await payload.member.send(content=f'Dir wurde die Discord Rolle "{role}" entzogen.')
        elif payload.emoji == discord.utils.get(await self.guild.fetch_emojis(), name='mayo'):  # Mayo
            role = discord.utils.get(roles, name='Team Mayo')
            if role not in payload.member.roles:
                await payload.member.add_roles(role)
                await payload.member.send(content=f'Du hast die Discord Rolle "{role}" erhalten.')
            else:
                await payload.member.remove_roles(role)
                await payload.member.send(content=f'Dir wurde die Discord Rolle "{role}" entzogen.')
        await self.raid_team_message.remove_reaction(payload.emoji, payload.member)


    @commands.Cog.listener()
    async def on_ready(self):
        guilds = []
        async for guild in self.bot.fetch_guilds():
            guilds.append(guild)
        self.guild = guilds[0]
        emojis = await self.guild.fetch_emojis()
        channels_on_server = await guilds[0].fetch_channels()
        self.rolechannel = discord.utils.get(channels_on_server, name='get-roles')
        if self.raid_team_message_id is not None:
            try:
                self.raid_team_message = await self.rolechannel.fetch_message(self.raid_team_message_id)
            except Exception as e:
                self.raid_team_message_id = None
                print(e)
        if self.raid_team_message_id is None:
            self.raid_team_message = await self.rolechannel.send('Bitte wähle anhand der untenstehenden Emojis in welchem Raidteam du raiden möchtest. Du kannst dich für beide Raid Teams eintragen. die Auswahl hier bedeutet nicht, dass du auch sicher im entsprechenden Team mitraiden kannst.')
            await self.raid_team_message.add_reaction(emoji=discord.utils.get(emojis, name='ketchup'))
            await self.raid_team_message.add_reaction(emoji=discord.utils.get(emojis, name='mayo'))
            self.raid_team_message_id = self.raid_team_message.id
            with open('raid_team.txt', 'w') as f:
                f.write(str(self.raid_team_message.id))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        payloadchannel = await self.bot.fetch_channel(payload.channel_id)
        if payloadchannel == self.rolechannel and not payload.member == self.bot.user:
            if payload.message_id == self.raid_team_message_id:
                await self.raid_team_role(payload)



