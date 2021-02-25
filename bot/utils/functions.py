import discord
from datetime import datetime


async def try_delete(message):
    try:
        await message.delete()
    except (discord.Forbidden, discord.NotFound, discord.HTTPException):
        pass


def create_default_embed(ctx, **options) -> discord.Embed:
    if options.get('color'):
        embed = discord.Embed(**options)
    else:
        embed = discord.Embed(color=discord.Color(int('0x2F3136', base=16)), **options)
    bot = ctx.bot
    embed.set_author(name=ctx.message.author.display_name, icon_url=str(ctx.message.author.avatar_url))
    embed.set_footer(text=bot.user.name, icon_url=str(bot.user.avatar_url))
    embed.timestamp = datetime.utcnow()
    return embed
