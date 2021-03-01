from discord.ext import commands
import pendulum
import discord


class Info(commands.Cog):
    """Commands that contain information about the bot."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='info', aliases=['botinfo'])
    async def info(self, ctx):
        """Displays information about the bot!"""
        embed = ctx.embed
        embed.title = f'{self.bot.name} Information!'
        # bot info: creator
        embed.add_field(name='Bot Info!', value=f'Creator: Dr Turtle#1771\n'
                                                f'Name: {self.bot.name}\n'
                                                f'Source: [Here!](https://github.com/1drturtle/mybot)')
        # discord info: guilds, members
        embed.add_field(name='Discord Info!', value=f'Server Count: `{len(self.bot.guilds)}`\n'
                                                    f'Member Count: `{sum([g.member_count for g in self.bot.guilds])}`')
        # other: cogs/total commands
        cmd_count = sum([1 for cmd in self.bot.walk_commands()])
        embed.add_field(name='Command Info!', value=f'`{len(self.bot.extensions)}` extensions loaded\n'
                                                    f'`{cmd_count}` total commands loaded.')

        return await ctx.send(embed=embed)

    @commands.command(name='member', aliases=['memberinfo'])
    @commands.guild_only()
    async def memberinfo(self, ctx, who: discord.Member = None):
        """
        Gets information about a member in the server.

        `who` - The member to get information about. Will use yourself if no member is specified.
        """
        embed = ctx.embed
        if who is None:
            who = ctx.author
        embed.title = f'{who.display_name} Member Info!'
        embed.set_thumbnail(url=str(who.avatar_url))
        # general: name, id, nick
        embed.add_field(
            name='General Info',
            value=f'**Name:** {who.name}\n'
                  f'**Nick:** {who.display_name}\n'
                  f'**ID:** `{who.id}`',
            inline=False
        )
        # timestamps: acc created, join time
        acc_create = pendulum.instance(who.created_at)
        joined_server = pendulum.instance(who.joined_at)
        embed.add_field(
            name='Time Info',
            value=f'**Account Created:** {acc_create.to_day_datetime_string()} \n({acc_create.diff_for_humans()} ago)\n'
                  f'**Joined Server:** {joined_server.to_day_datetime_string()} \n({joined_server.diff_for_humans()})',
            inline=False
        )
        # permissions: highest role, is owner of guild
        embed.add_field(
            name='Permissions',
            value=f'**Highest Role:** {who.top_role.mention}\n'
                  f'**Guild Owner:** {":white_check_mark:" if who.id == ctx.guild.owner_id else ":no_entry_sign:"}',
            inline=False
        )
        # mutual: # of mutual servers
        # embed.add_field(name='Other', value=f'Mutual Servers: {len(who.mutual_guilds)}')

        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
