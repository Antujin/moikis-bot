from discord.ext import commands
import discord
import yaml
import datetime
from Modules.helpers import is_in_channel, WrongChannel

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
                if self.votes is None:
                    self.votes = {}
        except Exception:
            pass


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id in self.votes.keys():
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if not payload.member == message.author:
                await self.vote_handler(payload)
                await message.remove_reaction(payload.emoji, payload.member)
                print(self.votes)



    @commands.command()
    @commands.has_role('Mega Oida')
    async def makepoll(self, ctx, poll):
        question, all_answers = poll.split('=')
        print(question)
        answers = all_answers.split(';')
        options = {}
        for i, answer in enumerate(answers):
            options.update({self.emojis[i]: answer})
        embed = discord.Embed(title=question, description=f'', color=0xff0000)
        for key in options.keys():
            embed.add_field(name=key, value=options[key], inline=False)
        msg = await ctx.send(content='', embed=embed)
        self.votes.update({msg.id: {'text': question,
                                    'options': options,
                                    'channel': ctx.channel.id,
                                    'voters': {},
                                    }})
        with open('voting.yml', 'w') as f:
            yaml.safe_dump(self.votes, f)
        for key in options.keys():
            await msg.add_reaction(key)
        await ctx.author.send(content=f'Umfrage erfolgreich im Channel `{ctx.channel.name}` erstellt.\nFür die Auswertung verwende bitte folgenden Befehl:\n`$evalpoll {msg.id}`\nUm die Umfrage zu löschen verwende den Befehl\n`$deletepoll {msg.id}`')
        await ctx.message.delete()


    @commands.command()
    @is_in_channel('offi-chat')
    async def evalpoll(self, ctx, pollid: int):
        if pollid not in self.votes.keys():
            await ctx.send(f'Ich kenne keine Umfrage mit der ID {pollid}.')
            return
        total_responses = len(self.votes[pollid]['voters'].keys())
        answers = {}
        for voterid in self.votes[pollid]['voters'].keys():
            vote = self.votes[pollid]['voters'][voterid]
            voter = ctx.message.guild.get_member(voterid)
            if vote not in answers.keys():
                answers.update({vote: [voter.name]})
            else:
                answers[vote].append(voter.name)
        embed = discord.Embed(title=f'Umfrageergebnisse bei {total_responses} Abstimmenden',
                              description=self.votes[pollid]['text'],
                              color=0x0000ff)
        for answer in answers.keys():
            if answers[answer] == []:
                embed.add_field(
                    name=f' {self.votes[pollid]["options"][answer]}: {len(answers[answer])} Stimmme(n) ({round(len(answers[answer]) / total_responses * 100, 2)}%)',
                    value='/', inline=True)
            else:
                embed.add_field(
                    name=f' {self.votes[pollid]["options"][answer]}: {len(answers[answer])} Stimmmen ({round(len(answers[answer]) / total_responses * 100, 2)}%)',
                    value='\n'.join(answers[answer]), inline=True)
        await ctx.send(f"Ausgewertet am {datetime.datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')}", embed=embed)
        #await ctx.message.delete()

    @commands.command()
    @is_in_channel('offi-chat')
    async def deletepoll(self, ctx, pollid: int):
        channel = ctx.message.guild.get_channel(self.votes[pollid]['channel'])
        msg = await channel.fetch_message(pollid)
        await msg.delete()
        with open(f'backup_poll_{pollid}.yml','w') as f:
            yaml.safe_dump(self.votes[pollid],f)
        del self.votes[pollid]
        with open('voting.yml', 'w') as f:
            yaml.safe_dump(self.votes, f)
        await ctx.send('Umfrage gelöscht.')
        #await ctx.message.delete()