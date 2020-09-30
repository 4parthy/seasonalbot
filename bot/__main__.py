import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from bot.bot import bot
from bot.constants import Client, STAFF_ROLES, WHITELISTED_CHANNELS
from bot.utils.decorators import in_channel_check
from bot.utils.extensions import walk_extensions
from bot.utils.extensions import EXTENSIONS


sentry_logging = LoggingIntegration(
    level=logging.DEBUG,
    event_level=logging.WARNING
)

sentry_sdk.init(
    dsn=Client.sentry_dsn,
    integrations=[sentry_logging]
)

log = logging.getLogger(__name__)

bot.add_check(in_channel_check(*WHITELISTED_CHANNELS, bypass_roles=STAFF_ROLES))

# for ext in walk_extensions():
#    bot.load_extension(ext)

for ext in EXTENSIONS:
    # print(ext)
    if ext.startswith('bot.exts.halloween'):
        bot.load_extension(ext)
    if ext.startswith('bot.exts.evergreen.error_handler'):
        bot.load_extension(ext)

bot.run(Client.token)
