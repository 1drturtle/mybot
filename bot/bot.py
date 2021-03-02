import asyncio
import logging
import sys
import traceback
from collections import Counter
import os

import aiofiles
import asyncpg
import discord
import pendulum
from discord.ext import commands
from discord.ext import tasks
import aiohttp

import config
from utils.functions import try_delete
from utils.context import CustomContext

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[{asctime}] [{levelname}] | {name}: {message}', style='{'))
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

# Make discord logs a bit quieter
logging.getLogger('discord.gateway').setLevel(logging.WARNING)
logging.getLogger('discord.client').setLevel(logging.WARNING)
logging.getLogger('discord.http').setLevel(logging.INFO)

log = logging.getLogger(__name__)


async def get_prefix(bot_, message: discord.Message):
    prefixes = [config.PREFIX]
    # first things first, no prefix for jsk
    if message.author.id in bot_.owner_ids and not bot_.owner_use_prefix \
            and message.content.startswith('jsk'):
        prefixes.append('')

    # if we're not in a guild, let's return default prefix
    if not message.guild:
        return commands.when_mentioned_or(*prefixes)(bot_, message)

    # grab from cache
    prefixes.append(bot_.prefixes.get(message.guild.id, config.PREFIX))
    return commands.when_mentioned_or(*prefixes)(bot_, message)


intents = discord.Intents.default()

COGS = {
    'cogs.errors', 'jishaku',
    'cogs.admin', 'cogs.utils', 'cogs.owner', 'cogs.tags', 'cogs.math', 'cogs.fun',
    'cogs.help', 'cogs.info'
}


class CustomBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            allowed_mention=discord.AllowedMentions.none(),
            owner_ids={config.DEV_ID, },
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

        # create async http client
        self.session = self.loop.run_until_complete(
            self.get_client_session()
        )

        # Let's setup the cache
        self.prefixes = dict(self.loop.run_until_complete(
            self.db.fetch("SELECT id, prefix FROM prefixes")
        ))
        log.info('Prefixes Loaded')

        self.blacklisted = set([x.get('id') for x in self.loop.run_until_complete(
            self.db.fetch("SELECT id FROM blacklist")
        )])
        log.info('Blacklist Loaded')

        self.commands_used = Counter()
        self.dump_command_metrics.start()

        # no prefix for owner toggle
        self.owner_use_prefix = False

        # Load Extensions (Cogs)
        for cog in COGS:
            try:
                self.load_extension(cog)
            except Exception as e:
                log.error(f'Cog {cog} failed to load!')
                traceback.print_exc()
        log.info('All Cogs Loaded!')

    @property
    def uptime(self):
        return pendulum.now(tz=pendulum.tz.UTC) - self.start_time

    @tasks.loop(minutes=5)
    async def dump_command_metrics(self):
        now = pendulum.now(tz=pendulum.tz.get_local_timezone())
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
        file_path = os.path.join(file_path, f'COMMAND_LOG_{now.format("YYYY_MM_DDTHH_mm_ss")}.log')
        content = f'Command statistics from an hour ago until {now}.\n'
        for value, count in self.commands_used.most_common():
            content += f'Command `{value}`, used {count} time{"s" if count != 1 else ""}\n'
        log.debug('running command metrics dump')
        async with aiofiles.open(file_path, mode='w+') as f:
            await f.write(content)
        self.commands_used = Counter()

    @dump_command_metrics.before_loop
    async def before_loop_cmd_metrics(self):
        await self.wait_until_ready()
        log.info('Starting Command Metrics Loop')

    async def run_command_metrics(self, ctx):
        # update global command usage
        self.commands_used[ctx.command.qualified_name] += 1

        # update individual command metrics
        await self.db.execute(
            "INSERT INTO command_usage (id, commands_used) values ($1, 1)"
            "ON CONFLICT (id) DO UPDATE SET commands_used = command_usage.commands_used + 1",
            ctx.author.id
        )
        log.debug(f'{ctx.author} ran command {ctx.command.qualified_name}')

    async def get_context(self, message, *, cls=CustomContext):
        return await super().get_context(message, cls=cls)

    async def get_client_session(self):
        return aiohttp.ClientSession(loop=self.loop)

    # close our HTTP session when we close the bot.
    async def close(self):
        await super().close()
        await self.session.close()
        await self.dump_command_metrics.cancel()


bot = CustomBot()


@bot.event
async def on_ready():
    log.info(f'Bot is ready!\n'
             f'{"-"*20} \n'
             f'Username: {bot.user.display_name}\n'
             f'Prefix: `{config.PREFIX}`\n'
             f'{"-"*20}')


@bot.event
async def on_message(message):
    author = message.author
    if author.bot:
        return

    if author.id in bot.blacklisted:
        logging.getLogger('owner').debug(f'Ignoring message from blacklisted user {author.name + author.discriminator}')
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


@bot.event
async def on_guild_join(guild):
    log.debug(f'Joined guild {guild.name} ({guild.id})')
    if len(bot.guilds) - 1 >= 95:
        try:
            await guild.owner.send('Sorry for the DM! I unfortunately had to leave your server because I have hit the'
                                   'limit of servers I can be in.')
        except:
            pass
        await guild.leave()
        log.info(f'Leaving Guild {guild.name} ({guild.id}) due to max limit.')

if __name__ == '__main__':
    bot.run(config.TOKEN)
