from discord.ext import commands
from utils.functions import create_default_embed
import config
import logging

log = logging.getLogger(__name__)


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='prefix')
    @commands.guild_only()
    async def prefix(self, ctx, prefix: str = None):
        """
        With no prefix specified, will send the current prefix. If a prefix to change is specified, it will change
        the prefix for this server assuming you have Manage Server permissions.

        `prefix` - The prefix to add. Will display current prefix if not provided.
        """
        embed = create_default_embed(ctx)
        if prefix:
            if not ctx.author.guild_permissions.manage_guild:
                raise commands.MissingPermissions(['manage_guild'])
            # update cache
            self.bot.prefixes[ctx.guild.id] = prefix
            # update DB
            await self.bot.db.execute(
                "INSERT INTO prefixes(id, prefix)\n"
                "VALUES($1, $2)\n"
                "ON CONFLICT ON CONSTRAINT guild_id\n"
                "  DO UPDATE set id=prefixes.id, prefix=EXCLUDED.prefix;",
                ctx.guild.id,
                prefix
            )
            log.debug(f'Prefix for guild {ctx.guild.name} ({ctx.guild.id}) changed to {prefix}')
            embed.title = 'Guild Prefix Changed!'
            embed.description = f'The server prefix has been set to `{prefix}`'
            return await ctx.send(embed=embed)

        current_prefix = self.bot.prefixes.get(ctx.guild.id, config.PREFIX)

        embed.title = 'Guild Prefix'
        embed.description = f'The prefix for {ctx.guild.name} is currently `{current_prefix}`'
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(AdminCommands(bot))
