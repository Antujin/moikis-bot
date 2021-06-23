from discord.ext import commands, tasks
import discord
import time

class ChannelManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pvp_position = 0
        self.m_position = 0
        self.categorychannel = None
        self.guild = None
        self.created_channels_mythic = []
        self.created_channels_other = []
        self.created_channels_pvp = []
        self.other_channelnames = ['🌈 RAINBOW BIDIBI', '🍻 Therapietheke', '🔨 Not Quite Right', '🍆 Not A Dildo', '🍹 Lästerschwestern']
        self.channelcreator.start()

    def get_M_channels(self):
        voice_channels = {}
        for channel in self.bot.get_all_channels():
            if channel.type == discord.ChannelType.voice and '⏳ M+' in channel.name:
                voice_channels.update({channel.name: channel})
            else:
                continue
        return voice_channels

    def get_PvP_channels(self):
        voice_channels = {}
        for channel in self.bot.get_all_channels():
            if channel.type == discord.ChannelType.voice and '⚡ PvP blasten' in channel.name:
                voice_channels.update({channel.name: channel})
            else:
                continue
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
        if '⏳ M+' not in m_channels.keys():
            await self.guild.create_voice_channel(name='⏳ M+', category=self.categorychannel, position=2, bitrate=96000)
            return
        self.m_position = m_channels['⏳ M+'].position
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
                    new_channel = await self.guild.create_voice_channel(name=new_channelname,
                                                                        category=self.categorychannel,
                                                                        position=self.m_position + i - 1,
                                                                        bitrate=96000)
                    self.created_channels_mythic.append(new_channel)
                    created = True
                else:
                    i += 1
            return
        i = 0
        while empty_channels > 1:
            channel = deletable_channels[i]
            if channel in self.created_channels_mythic or not channel.name == '⏳ M+':
                await channel.delete()
                empty_channels -= 1
                deletable_channels.remove(channel)
                if not self.created_channels_mythic == []:
                    self.created_channels_mythic.remove(channel)
            else:
                i += 1

    async def create_pvp_channel(self):
        pvp_channels = self.get_PvP_channels()
        empty_channels = 0
        deletable_channels = []
        if '⚡ PvP blasten' not in pvp_channels.keys():
            await self.guild.create_voice_channel(name='⚡ PvP blasten', category=self.categorychannel, position=2+len(self.get_M_channels()),
                                                 bitrate=96000)
            return
        self.pvp_position = pvp_channels['⚡ PvP blasten'].position
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
                    new_channel = await self.guild.create_voice_channel(name=new_channelname,
                                                                        category=self.categorychannel, position=self.pvp_position+i-1,
                                                                        bitrate=96000)
                    self.created_channels_pvp.append(new_channel)
                    created = True
                else:
                    i += 1
            return
        i = 0
        while empty_channels > 1:
            channel = deletable_channels[i]
            if channel in self.created_channels_pvp or not channel.name == '⚡ PvP blasten':
                await channel.delete()
                empty_channels -= 1
                deletable_channels.remove(channel)
                if not self.created_channels_pvp == []:
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


    @tasks.loop(seconds=5)
    async def channelcreator(self):
        await self.create_mythic_channel()
        await self.create_pvp_channel()
        #await self.create_other_channel()

    @channelcreator.before_loop
    async def before_channelcreator(self):
        print('waiting...')
        await self.bot.wait_until_ready()
        guilds = []
        async for guild in self.bot.fetch_guilds():
            guilds.append(guild)
        self.guild = guilds[0]
        channels_on_server = await guilds[0].fetch_channels()
        self.categorychannel = discord.utils.get(channels_on_server, name='🌌 World of Warcraft 🌌')
        print('Starting Loop...')
