from discord.ext import commands


class Todo(commands.Cog):
    """Commands for the To-Do list."""
    def __int__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Todo(bot))
