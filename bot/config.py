import os
import json

# -- Required --
TOKEN = os.getenv('DISCORD_BOT_TOKEN', None)
POSTGRES_DATA = json.loads(os.getenv('DISCORD_DB_DATA', '{}'))

# -- Optional --
# --------------

PREFIX = os.getenv('DISCORD_BOT_PREFIX', '-')
DEV_ID = int(os.getenv('DISCORD_DEV_ID', '175386962364989440'))
DEFAULT_STATUS = os.getenv('DISCORD_STATUS', f'{PREFIX}help')

# Version
VERSION = os.getenv('VERSION', 'testing')

# Error Reporting
SENTRY_URL = os.getenv('SENTRY_URL', None)
ENVIRONMENT = os.getenv('ENVIRONMENT', 'testing')
