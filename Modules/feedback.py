from discord.ext import commands
import discord
import datetime

class Feedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        output_channel = discord.utils.get(self.bot.guilds[0].channels, name='offi-chat')
        if message.author == self.bot.user:
            return
        if message.channel.type == discord.ChannelType.private:
            mention = discord.utils.get(self.bot.guilds[0].roles, name='Mega Oida')
            embed = discord.Embed(title='Feedback', description=f'Erhalten am {datetime.datetime.now().strftime("%d.%m.%Y um %H:%M Uhr")}', color=0x00ff00)
            embed.add_field(name='Nachricht:', value=message.content, inline=False)
            await output_channel.send(f'{mention.mention}', embed=embed)
            await message.channel.send('Hallo, \nNachricht erhalten und and die Offis weitergeleitet. Du wirst keine direkte Antwort auf dein Feedback erhalten, da deine Nachricht anonymisiert wurde.')
            return