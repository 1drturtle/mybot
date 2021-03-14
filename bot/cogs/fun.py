import random

from discord.ext import commands


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
