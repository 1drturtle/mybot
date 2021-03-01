from discord.ext import commands
import aiohttp
import discord
import d20


class Math(commands.Cog):
    """Commands to do Math in the bot."""
    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.initialize())
        self.session = None

    async def initialize(self):
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        self.task.cancel()
        self.session.close()

    @commands.command(name='math')
    async def math_cmd(self, ctx, *, query: str):
        """
        Does math.

        `query` - The math to evaluate.
        """
        data = {
            'expr': query,
        }
        result = await self.session.post(url='http://api.mathjs.org/v4/',
                                         json=data)
        result = await result.json()
        print(result)
        embed = ctx.embed
        embed.add_field(name='Query', value=f'```xl\n{query}\n```')
        if result['result'] is None:
            embed.colour = discord.Colour.red()
            embed.title = 'Math Error!'
            embed.add_field(name='Error', value=f'```diff\n- {result["error"]} -\n```')
        else:
            embed.colour = discord.Colour.green()
            embed.title = 'Math Result'
            embed.add_field(name='Result', value=f'```xl\n{result["result"]}\n```')
        return await ctx.send(embed=embed)

    @commands.command(name='roll', aliases=['dice', 'r'])
    async def roll_cmd(self, ctx, *, dice_str: str):
        """
        Rolls a dice string.

        `dice_str` - The dice to roll.
        """
        embed = ctx.embed
        embed.add_field(name='Dice String', value=f'```\n{dice_str}\n```', inline=False)
        try:
            result = d20.roll(dice_str)
        except d20.RollError as e:
            embed.colour = discord.Colour.red()
            embed.title = 'Dice Error!'
            embed.add_field(name='Error', value=f'```diff\n- {e} -\n```')
        else:
            embed.title = 'Dice Result'
            output = result.result
            if len(output) > 1024:
                output = f'{output[:800]}...\n**Total**: {result.total}'
            embed.add_field(name='Result', value=output)
            embed.colour = discord.Colour.green()
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Math(bot))
