from discord.ext import commands
import discord
import yaml


class Voting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = None
        self.votes = {}
        self.emojis = ['0️⃣','1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']





    async def vote_handler(self, payload):
        if payload.emoji.name in self.votes[payload.message_id]['options'].keys():
            self.votes[payload.message_id]['voters'].update({payload.member.id: payload.emoji.name})
            await payload.member.send(f"Deine Stimme für '{self.votes[payload.message_id]['options'][payload.emoji.name]}' wurde erfolgreich registriert.")
            with open('voting.yml','w') as f:
                yaml.safe_dump(self.votes, f)


    @commands.Cog.listener()
    async def on_ready(self):
        guilds = []
        async for guild in self.bot.fetch_guilds():
            guilds.append(guild)
        self.guild = guilds[0]
        channels_on_server = await guilds[0].fetch_channels()
        try:
            with open('voting.yml', 'r') as f:
                self.votes = yaml.safe_load(f)
        except Exception:
            channel = discord.utils.get(channels_on_server, name='test')
            message = await channel.send('Hallo Welt')
            self.votes.update({message.id: {'text': message.content,
                                            'options': {},
                                            'voters': {},
                                            }})
            for i in range(11):
                self.votes[message.id]['options'].update({self.emojis[i]: f'Option {i}'})
                await message.add_reaction(self.emojis[i])

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id in self.votes.keys():
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if not payload.member == message.author:
                await self.vote_handler(payload)
                await message.remove_reaction(payload.emoji, payload.member)
                print(self.votes)
