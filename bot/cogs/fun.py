from discord.ext import commands
import random


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
        won, lost = 'You won the game!', 'You lost the game!'

        # rock beats scissors, dies to paper
        # scissors beats paper, dies to rock
        # paper beats rock, dies to scissors
        if choice == bot_choice:
            embed.description = 'You picked the same thing as the bot! Try Again!'
            return await ctx.send(embed=embed)

        if (user_rock := choice == 'rock') and bot_choice == 'scissors' \
                or bot_choice == 'rock' and choice == 'scissors':
            if user_rock:
                embed.description = won
            else:
                embed.description = lost
        elif (user_scissors := choice == 'scissors') and bot_choice == 'paper' \
                or bot_choice == 'scissors' and choice == 'paper':
            if user_scissors:
                embed.description = won
            else:
                embed.description = lost
        elif (user_paper := choice == 'paper') and bot_choice == 'rock' \
                or bot_choice == 'paper' and choice == 'rock':
            if user_paper:
                embed.description = won
            else:
                embed.description = lost

        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
