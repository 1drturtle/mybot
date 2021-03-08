import asyncio
import random
import typing

import discord
from discord.ext import commands

from .cards.blackjack import *


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
    return out[:10] # first ten


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

    @commands.command(name='blackjack', aliases=['bkj'])
    @commands.max_concurrency(1, commands.BucketType.channel)
    @commands.guild_only()
    async def blackjack(self, ctx):
        """Plays blackjack!"""
        # --------
        # create join embed & send reactions

        join_embed = ctx.embed
        join_embed.title = 'Join Blackjack!'
        join_embed.description = 'React with \U0001f44d in the next 30 seconds to play Blackjack!\n' \
                                 'Max 10 players.'
        join_msg: discord.Message = await ctx.send(embed=join_embed)
        await join_msg.add_reaction('\U0001f44d')

        # -------
        # get the players, clear reactions, and edit embed

        members = await wait_for_reactions(join_msg, '\U0001f44d', 30)
        await join_msg.clear_reactions()
        join_embed.description = f'Time expired! Starting the game in 10...\n' \
                                 f'Players: {", ".join(p.mention for p in members)}'
        await join_msg.edit(embed=join_embed)
        await asyncio.sleep(10)
        await join_msg.delete(delay=3)

        # -------
        # start the game
        # TODO: implement betting
        # TODO: implement PIL-based cards

        game_running = True
        game_embed = ctx.embed
        game_embed.title = 'Blackjack'
        game_embed_msg = None

        # make players
        players = [Player(m) for m in members]
        dealer = Dealer()
        deck = Deck()

        def player_list():
            all_members = players + [dealer]
            biggest_name = max([len(x.name) for x in all_members])
            biggest_cards = max(len(x.card_display) for x in all_members)
            return '```md\n' + '\n'.join(x.pretty_str(biggest_name, biggest_cards) for x in all_members) + '\n```'

        # game loop
        while game_running:
            # reset cards
            for player in players:
                player.cards = []
            dealer.cards = []
            # reset deck if next turn would bring len <= 28
            next_turn_deck_length = deck.card_count - (2 * len(players) + 1)
            if next_turn_deck_length <= 28:
                deck = Deck()
            # deal cards
            dealer.cards = [deck.draw(), deck.draw()]
            for player in players:
                player.cards = [deck.draw(), deck.draw()]
            # construct & send turn embed
            game_embed.description = player_list()
            game_embed_msg = await ctx.send(embed=game_embed)
            # go through each player and get their turn action (hit or pass), ignoring busted
            for player in players:
                if player.busted:
                    continue
            # if all pass, end game
            # debug stop loop
            game_running = False


def setup(bot):
    bot.add_cog(Fun(bot))
