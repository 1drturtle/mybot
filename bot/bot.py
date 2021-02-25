import asyncio
import logging
import sys
import traceback

import asyncpg
import discord
import pendulum
from discord.ext import commands

import config

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
    'cogs.admin', 'cogs.utils',
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
            self.db.fetch("SELECT id, prefix from prefixes")
        ))

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


bot = CustomBot()


@bot.event
async def on_ready():
    log.info(f'\nBot is ready! \n'
             f'{"-"*20} \n'
             f'Username: {bot.user.display_name}\n'
             f'Prefix: {config.PREFIX}\n'
             f'{"-"*20}')


if __name__ == '__main__':
    bot.run(config.TOKEN)
