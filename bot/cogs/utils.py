from discord.ext import commands
import pendulum
from utils.functions import create_default_embed


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='uptime', aliases=['up', 'alive'])
    async def uptime(self, ctx):
        """Shows the uptime of the bot."""
        embed = create_default_embed(ctx)
        embed.title = f'{self.bot.name} Uptime'
        embed.add_field(name='Current Uptime', value=f'```fix\n{self.bot.uptime.in_words()}\n```')
        return await ctx.send(embed=embed)

    @commands.command(name='ping')
    @commands.cooldown(5, 5, type=commands.BucketType.user)
    async def ping(self, ctx):
        """Shows the latency of the bot."""
        embed = create_default_embed(ctx)
        # add bot ping
        embed.title = f'{self.bot.name} Ping'
        embed.add_field(name='Bot Ping', value=f'```fix\n{round(self.bot.latency * 1000)} ms\n```')
        # time sending message
        websocket = pendulum.now()
        msg = await ctx.send(embed=embed)
        websocket = pendulum.now() - websocket
        # edit embed for discord ping and send
        embed.add_field(name='Discord Ping', value=f'```fix\n{round(websocket.total_seconds() * 1000)} ms\n```')
        return await msg.edit(embed=embed)


def setup(bot):
    bot.add_cog(Utils(bot))
