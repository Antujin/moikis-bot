import locale
import logging
import os
import datetime

import discord
from discord.ext import tasks, commands

from Modules import PublishSheets
from Modules import Raidhelper2Sheets

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter((logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')))
logger.addHandler(handler)

locale.setlocale(locale.LC_TIME, "de_DE.utf8")


class WrongChannel(commands.CheckFailure):
    pass


def is_in_channel(channelname):
    async def predicate(ctx):
        if not ctx.channel.name == channelname:
            raise WrongChannel(f'Dieser Befehl funktioniert nur im Channel "{channelname}"')
        return True
    return commands.check(predicate)

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
    @is_in_channel('offi-chat')
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

class ChannelManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.created_channels_mythic = []
        self.created_channels_other = []
        self.created_channels_pvp = []
        self.other_channelnames = ['🌈 RAINBOW BIDIBI', '🍻 Therapietheke', '🔨 Not Quite Right', '🍆 Not A Dildo', '🍹 Lästerschwestern']
        self.channelcreator.start()

    def get_M_channels(self):
        voice_channels = {}
        for channel in self.bot.get_all_channels():
            if channel.type == discord.ChannelType.voice and 'M+' in channel.name:
                voice_channels.update({channel.name: channel})
            else:
                continue
        #print(voice_channels)
        return voice_channels

    def get_PvP_channels(self):
        voice_channels = {}
        for channel in self.bot.get_all_channels():
            if channel.type == discord.ChannelType.voice and 'PvP blasten' in channel.name:
                voice_channels.update({channel.name: channel})
            else:
                continue
        print(voice_channels)
        return voice_channels

    def get_other_channels(self):
        voice_channels = {}
        for channel in self.bot.get_all_channels():
            if channel.type == discord.ChannelType.voice and channel.name in self.other_channelnames:
                voice_channels.update({channel.name: channel})
            else:
                continue
        return voice_channels

    def cog_unload(self):
        self.channelcreator.cancel()


    async def create_mythic_channel(self):
        m_channels = self.get_M_channels()
        empty_channels = 0
        deletable_channels = []
        for channelname in m_channels.keys():
            if m_channels[channelname].members == []:
                empty_channels += 1
                deletable_channels.append(m_channels[channelname])
        if empty_channels == 0:
            created = False
            i = 2
            while not created:
                new_channelname = f'⏳ M+ {i}'
                if not new_channelname in m_channels.keys():
                    new_channel = await m_channels['⏳ M+ 1'].clone(name=new_channelname)
                    await new_channel.edit(position=m_channels['⏳ M+ 1'].position+i-1)
                    self.created_channels_mythic.append(new_channel)
                    created = True
                else:
                    i += 1
            return
        i = 0
        while empty_channels > 1:
            channel = deletable_channels[i]
            if channel in self.created_channels_mythic:
                await channel.delete()
                empty_channels -= 1
                deletable_channels.remove(channel)
                self.created_channels_mythic.remove(channel)
            else:
                i += 1

    async def create_pvp_channel(self):
        pvp_channels = self.get_PvP_channels()
        empty_channels = 0
        deletable_channels = []
        for channelname in pvp_channels.keys():
            if pvp_channels[channelname].members == []:
                empty_channels += 1
                deletable_channels.append(pvp_channels[channelname])
        if empty_channels == 0:
            created = False
            i = 2
            while not created:
                new_channelname = f'⚡ PvP blasten {i}'
                if not new_channelname in pvp_channels.keys():
                    new_channel = await pvp_channels['⚡ PvP blasten'].clone(name=new_channelname)
                    await new_channel.edit(position=pvp_channels['⚡ PvP blasten'].position + i - 1)
                    self.created_channels_pvp.append(new_channel)
                    created = True
                else:
                    i += 1
            return
        i = 0
        while empty_channels > 1:
            channel = deletable_channels[i]
            if channel in self.created_channels_pvp:
                await channel.delete()
                empty_channels -= 1
                deletable_channels.remove(channel)
                self.created_channels_pvp.remove(channel)
            else:
                i += 1
    async def create_other_channel(self):
        m_channels = self.get_other_channels()
        empty_channels = 0
        deletable_channels = []
        for channelname in m_channels.keys():
            if m_channels[channelname].members == []:
                empty_channels += 1
                deletable_channels.append(m_channels[channelname])
        if empty_channels == 0:
            created = False
            i = 1
            while not created:
                if i >= len(self.other_channelnames):
                    return
                new_channelname = self.other_channelnames[i]
                if not new_channelname in m_channels.keys():
                    new_channel = await m_channels['🌈 RAINBOW BIDIBI'].clone(name=new_channelname)
                    await new_channel.edit(position=m_channels['🌈 RAINBOW BIDIBI'].position + i)
                    self.created_channels_other.append(new_channel)
                    created = True
                else:
                    i += 1
            return
        i = 0
        while empty_channels > 1:
            channel = deletable_channels[i]
            if channel in self.created_channels_other:
                await channel.delete()
                empty_channels -= 1
                deletable_channels.remove(channel)
                self.created_channels_other.remove(channel)
            else:
                i += 1


    @tasks.loop(seconds=2)
    async def channelcreator(self):
        await self.create_mythic_channel()
        await self.create_pvp_channel()
        #await self.create_other_channel()

    @channelcreator.before_loop
    async def before_channelcreator(self):
        print('waiting...')
        await self.bot.wait_until_ready()
        print('Starting Loop...')


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

