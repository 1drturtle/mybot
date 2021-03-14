import asyncio
import random
import typing

import discord
from discord.ext import commands

from .cards.blackjack import *
from utils.functions import try_delete


async def wait_for_reactions(msg: discord.Message, reaction_text: str, time=30) -> typing.List[discord.Member]:
    await asyncio.sleep(time)
    msg = await msg.channel.fetch_message(msg.id)
    out = []
    for reaction in msg.reactions:
        if not str(reaction.emoji) == reaction_text:
            continue
        for user in await reaction.users().flatten():
            if not user.bot:
                out.append(user)
    return out[:10]  # first ten


async def recursive_hit(deck: Deck, g_msg: discord.Message, g_embed: discord.Embed,
                        player: Player, p_list, ctx):
    """
    :return: List[Deck, Embed, Message, status: bool]
    """
    # Check Deck for Safety Add Card
    if deck.card_count <= 28:
        deck = Deck()
    # First Hit
    player.cards.append(deck.draw())
    if player.busted:
        g_embed.clear_fields()
        return [deck, g_embed, g_msg, None]
    # update
    await try_delete(g_msg)
    g_embed.description = p_list()
    g_embed.clear_fields()
    g_msg = await ctx.send(embed=g_embed)
    # Prompt for another hit if not busted
    question = await ctx.send('Would you like to hit again?\n'
                              'React with :white_check_mark: or :no_entry_sign:.')
    # add reactions to question and wait for response
    await question.add_reaction('\U00002705')
    await question.add_reaction('\U0001F6AB')

    def check(reaction, user):
        return user.id == player.player.id and str(reaction.emoji) in ['\U00002705', '\U0001F6AB']

    try:
        new_reaction, _ = await ctx.bot.wait_for('reaction_add', timeout=60, check=check)
    except asyncio.TimeoutError:
        await try_delete(question)
        await ctx.send('You waited too long! Your turn has been skipped.', delete_after=10)
        return [deck, g_embed, g_msg, 'timeout']

    await try_delete(question)

    # hit
    if str(new_reaction.emoji) == '\U00002705':
        return await recursive_hit(deck, g_msg, g_embed, player, p_list, ctx)
    # pass
    if str(new_reaction.emoji) == '\U0001F6AB':
        return [deck, g_embed, g_msg, 'pass']


class Fun(commands.Cog):
    """Some fun commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='rps', alias='rockpaperscissors')
    async def rps_cmd(self, ctx, choice: str):
        """
        Plays Rock-Paper-Scissors with the bot!

        `choice` - Rock, Paper, or Scissors
        """

        embed = ctx.embed
        embed.title = 'Rock, Paper, Scissors!'

        bot_choice = (choices := ['rock', 'paper', 'scissors'])[random.randint(0, 2)]

        if choice.lower() not in choices:
            raise commands.BadArgument('Choice must be Rock, Paper, or Scissors!')

        embed.add_field(name='Your Choice', value=choice.title())
        embed.add_field(name='Bot\'s Choice', value=bot_choice.title())

        # rock beats scissors, dies to paper
        # scissors beats paper, dies to rock
        # paper beats rock, dies to scissors
        if choice == bot_choice:
            embed.description = 'You picked the same thing as the bot! Try Again!'
            return await ctx.send(embed=embed)

        user_won = False
        if choice == 'rock' and bot_choice == 'scissors':
            user_won = True
        elif choice == 'scissors' and bot_choice == 'paper':
            user_won = True
        elif choice == 'paper' and bot_choice == 'rock':
            user_won = True

        if user_won:
            embed.description = f'You won the game! {choice.title()} beats {bot_choice.title()}'
        else:
            embed.description = f'You lost the game! {bot_choice.title()} beats {choice.title()}'

        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
