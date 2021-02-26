import asyncio
import logging
import sys
import traceback

import asyncpg
import discord
import pendulum
from discord.ext import commands

import config
from utils.functions import try_delete
from utils.context import CustomContext

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[{asctime}] [{levelname}] | {name}: {message}', style='{'))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Make discord logs a bit quieter
logging.getLogger('discord.gateway').setLevel(logging.WARNING)
logging.getLogger('discord.client').setLevel(logging.WARNING)

log = logging.getLogger(__name__)


async def get_prefix(bot, message: discord.Message):
    # first things first, no prefix for jsk
    if message.content.startswith('jsk') and message.author.id in bot.owner_ids:
        return ""

    # if we're not in a guild, let's return default prefix
    if not message.guild:
        return commands.when_mentioned_or(*config.PREFIX)(bot, message)

    # grab from cache
    return commands.when_mentioned_or(*bot.prefixes.get(message.guild.id, config.PREFIX))(bot, message)


intents = discord.Intents.default()

COGS = {
    'cogs.errors', 'jishaku',
    'cogs.admin', 'cogs.utils', 'cogs.owner', 'cogs.tags',
    'cogs.help'
}


class CustomBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            # help_command=None,
            allowed_mention=discord.AllowedMentions.none(),
            owner_ids={config.DEV_ID},
            **kwargs
        )

        # global name declaration
        self.name = 'TestBot'

        # Async Loop
        self.loop = asyncio.get_event_loop()

        # UTC time when bot started
        self.start_time = pendulum.now(tz=pendulum.tz.UTC)

        # Connect to PostgreSQL
        self.db = self.loop.run_until_complete(
            asyncpg.create_pool(
                **config.POSTGRES_DATA
            )
        )

        # Let's setup the cache
        self.prefixes = dict(self.loop.run_until_complete(
            self.db.fetch("SELECT id, prefix FROM prefixes")
        ))

        self.blacklisted = set([x.get('id') for x in self.loop.run_until_complete(
            self.db.fetch("SELECT id FROM blacklist")
        )])

        # Load Extensions (Cogs)
        for cog in COGS:
            try:
                self.load_extension(cog)
            except Exception as e:
                log.error(f'Cog {cog} failed to load!')
                traceback.print_exc()

    @property
    def uptime(self):
        return pendulum.now(tz=pendulum.tz.UTC) - self.start_time

    async def run_command_metrics(self, ctx):
        await self.db.execute(
            f'INSERT INTO command_usage (id, commands_used) values ({ctx.author.id}, 1)'
            f'ON CONFLICT (id) DO UPDATE SET commands_used = command_usage.commands_used + 1'
        )

    async def get_context(self, message, *, cls=CustomContext):
        return await super().get_context(message, cls=cls)


bot = CustomBot()


@bot.event
async def on_ready():
    log.info(f'\nBot is ready! \n'
             f'{"-"*20} \n'
             f'Username: {bot.user.display_name}\n'
             f'Prefix: {config.PREFIX}\n'
             f'{"-"*20}')


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.id in bot.blacklisted:
        return

    if not bot.is_ready():
        return

    context = await bot.get_context(message)
    if context.command is not None:
        return await bot.invoke(context)


@bot.event
async def on_command(ctx):

    await bot.run_command_metrics(ctx)

    if ctx.message.content.startswith('jsk'):
        return

    await try_delete(ctx.message)


if __name__ == '__main__':
    bot.run(config.TOKEN)
