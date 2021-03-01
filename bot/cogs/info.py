from discord.ext import commands


class Info(commands.Cog):
    """Commands that contain information about the bot."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='info', aliases=['botinfo'])
    async def info(self, ctx):
        """Displays information about the bot!"""
        embed = ctx.embed
        embed.title = f'{self.bot.name} Information!'
        # bot info: creator
        embed.add_field(name='Bot Info!', value=f'Creator: Dr Turtle#1771\n'
                                                f'Name: {self.bot.name}\n'
                                                f'Source: [Here!](https://github.com/1drturtle/mybot)')
        # discord info: guilds, members
        embed.add_field(name='Discord Info!', value=f'Server Count: `{len(self.bot.guilds)}`\n'
                                                    f'Member Count: `{sum([g.member_count for g in self.bot.guilds])}`')
        # other: cogs/total commands
        cmd_count = sum([1 for cmd in self.bot.walk_commands()])
        embed.add_field(name='Command Info!', value=f'`{len(self.bot.extensions)}` extensions loaded\n'
                                                    f'`{cmd_count}` total commands loaded.')

        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
