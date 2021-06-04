from discord.ext import commands

class WrongChannel(commands.CheckFailure):
    pass


def is_in_channel(channelname):
    async def predicate(ctx):
        if not ctx.channel.name == channelname:
            raise WrongChannel(f'Dieser Befehl funktioniert nur im Channel "{channelname}"')
        return True
    return commands.check(predicate)
