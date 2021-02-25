from discord.ext import commands


class Owner(commands.Cog):
    """Commands for the Owner of the Bot"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return ctx.author.id in self.bot.owner_ids

    @commands.command(name='say')
    async def say(self, ctx, *, message: str):
        """
        Repeats what you tell it.

        `message` - The message to repeat.
        """
        return await ctx.send(message)


def setup(bot):
    bot.add_cog(Owner(bot))
