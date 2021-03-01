import discord
import traceback
import sys
from discord.ext import commands
import logging
from utils.functions import create_default_embed
import pendulum

log = logging.getLogger(__name__)


class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """

        embed = create_default_embed(ctx, title='Command Error!', color=discord.Colour(0xDC143C))
        if ctx.command:
            cmd_name = f'`{ctx.prefix}{ctx.command.qualified_name}`'
        else:
            cmd_name = 'This command'

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound,)

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            embed.description = f'{cmd_name} has been disabled.'
            await ctx.send(embed=embed)

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                embed.description = f'{cmd_name} can not be used in Private Messages.'
                await ctx.author.send(embed=embed)
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = f'Missing required argument `{error.param.name}`.\n' \
                                f'Please check `{ctx.prefix}help {ctx.command.qualified_name}` for more information.'
            await ctx.send(embed=embed)

        elif isinstance(error, commands.CommandOnCooldown):
            cd = pendulum.duration(seconds=error.retry_after)
            embed.description = f'{cmd_name} is on cooldown! Try again in {cd.in_words()}!'
            await ctx.send(embed=embed)

        elif isinstance(error, commands.BadArgument):
            embed.description = f'Bad Argument! Double check `{ctx.prefix}help {ctx.command.qualified_name}`\n{error}'
            await ctx.send(embed=embed)

        elif isinstance(error, discord.Forbidden):
            try:
                embed.description = f'I do not have permissions to run {cmd_name} in that channel! Please double-check' \
                                    f'your permission settings!'
                await ctx.author.send(embed=embed)
            except:
                pass

        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            log.error('Ignoring exception in command {}:'.format(ctx.command))
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
