from discord.ext import commands
import discord
import typing
from utils.functions import create_default_embed
import datetime
import logging

log = logging.getLogger(__name__)


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

    @commands.command(name='blacklist')
    async def blacklist(self, ctx, who: typing.Union[discord.Member, discord.User], reason: str = None):
        """
        Blacklists a user from using the bot.
        """
        embed = create_default_embed(ctx)
        if who.id in self.bot.blacklisted:
            embed.colour = discord.Colour(0xDC143C)
            embed.title = 'Blacklist Error'
            embed.description = 'User is already blacklisted.'
            return await ctx.send(embed=embed)
        embed.title = 'User Blacklisted'
        embed.description = f'{who.name} has been blacklisted from using the Bot.'
        await self.bot.db.execute(
            f'INSERT INTO blacklist values ($1, $2, $3)',
            who.id,
            datetime.datetime.utcnow(),
            reason if reason else ''
        )
        self.bot.blacklisted.add(who.id)
        log.debug(f'Blacklisted {who.name + who.discriminator}')
        return await ctx.send(embed=embed)

    @commands.command(name='unblacklist')
    async def unblacklist(self, ctx, who: typing.Union[discord.Member, discord.User]):
        """
        Removes a user from the bot's blacklist
        """
        embed = create_default_embed(ctx)
        if who.id not in self.bot.blacklisted:
            embed.colour = discord.Colour(0xDC143C)
            embed.title = 'Blacklist Error'
            embed.description = 'User is not blacklisted.'
            return await ctx.send(embed=embed)
        embed.title = 'User removed from Blacklist'
        embed.description = f'{who.name} has been un-blacklisted from the Bot.'
        await self.bot.db.execute(
            f'DELETE FROM blacklist where id = $1', who.id
        )
        self.bot.blacklisted.remove(who.id)
        log.debug(f'{who.name + who.discriminator} removed from blacklist.')
        return await ctx.send(embed=embed)

    @commands.command(name='leave')
    async def leave_guild(self, ctx, guild_id: int):
        """Leaves a guild."""
        embed = ctx.embed
        guild = self.bot.get_guild(guild_id)
        if not guild:
            embed.title = 'Guild Error'
            embed.description = f'Could not find guild with id `{guild_id}`'

        embed.title = 'Leaving Guild!'
        embed.description = f'Leaving Guild {guild.name}'
        await guild.leave()
        log.info(f'Force-leaving guild {guild.name} ({guild.id}')
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Owner(bot))
