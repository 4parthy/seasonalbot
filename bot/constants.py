import enum
import logging
from datetime import datetime
from os import environ
from typing import NamedTuple

__all__ = (
    "AdventOfCode",
    "Branding",
    "Channels",
    "Client",
    "Colours",
    "Emojis",
    "Hacktoberfest",
    "Icons",
    "Lovefest",
    "Month",
    "Roles",
    "Tokens",
    "Wolfram",
    "MODERATION_ROLES",
    "STAFF_ROLES",
    "WHITELISTED_CHANNELS",
    "ERROR_REPLIES",
    "NEGATIVE_REPLIES",
    "POSITIVE_REPLIES",
)

log = logging.getLogger(__name__)


class AdventOfCode:
    leaderboard_cache_age_threshold_seconds = 3600
    leaderboard_id = 631135
    leaderboard_join_code = str(environ.get("SEASONALBOT_AOC_JOIN_CODE", None))
    leaderboard_max_displayed_members = 10
    year = int(environ.get("SEASONALBOT_AOC_YEAR", datetime.utcnow().year))
    role_id = int(environ.get("SEASONALBOT_AOC_ROLE_ID", 0))


class Branding:
    cycle_frequency = int(environ.get("SEASONALBOT_CYCLE_FREQUENCY", 3))  # 0: never, 1: every day, 2: every 2 days, ...


class Channels(NamedTuple):
    admins = int(environ.get("SEASONALBOT_ADMIN_CHANNEL_ID", 0))
    advent_of_code = int(environ.get("SEASONALBOT_AOC_CHANNEL_ID", 0))
    announcements = int(environ.get("SEASONALBOT_ANNOUNCEMENTS_CHANNEL_ID", 0))
    big_brother_logs = 0
    bot = int(environ.get("SEASONALBOT_BOT_CHANNEL_ID", 0))
    checkpoint_test = 0
    devalerts = 0
    devlog = int(environ.get("SEASONALBOT_DEVLOG_CHANNEL_ID", 0))
    dev_contrib = 0
    dev_branding = 0
    help_0 = 0
    help_1 = 0
    help_2 = 0
    help_3 = 0
    help_4 = 0
    help_5 = 0
    helpers = 0
    message_log = 0
    mod_alerts = 0
    modlog = 0
    off_topic_0 = int(environ.get("SEASONALBOT_OFFTOPIC_CHANNEL_ID", 0))
    off_topic_1 = int(environ.get("SEASONALBOT_OFFTOPIC_1_CHANNEL_ID", 0))
    off_topic_2 = int(environ.get("SEASONALBOT_OFFTOPIC_2_CHANNEL_ID", 0))
    python = 0
    reddit = 0
    seasonalbot_commands = int(environ.get("SEASONALBOT_COMMANDS_CHANNEL_ID", 0))
    seasonalbot_voice = int(environ.get("SEASONALBOT_VOICE_CHANNEL_ID", 0))
    staff_lounge = 0
    verification = 0
    python_discussion = 0
    show_your_projects = 0
    show_your_projects_discussion = 0
    hacktoberfest_2019 = 0


class Client(NamedTuple):
    guild = int(environ.get("SEASONALBOT_DISCORD_SERVER_ID", 0))
    prefix = environ.get("SEASONALBOT_PREFIX", ".")
    token = environ.get("SEASONALBOT_TOKEN")
    sentry_dsn = environ.get("SEASONALBOT_SENTRY_DSN")
    debug = environ.get("SEASONALBOT_DEBUG", "").lower() == "true"
    github_bot_repo = "https://github.com/4parthy/seasonalbot"
    # Override seasonal locks: 1 (January) to 12 (December)
    month_override = int(environ["SEASONALBOT_MONTH_OVERRIDE"]) if "SEASONALBOT_MONTH_OVERRIDE" in environ else None


class Colours:
    blue = 0x0279fd
    bright_green = 0x01d277
    dark_green = 0x1f8b4c
    orange = 0xe67e22
    pink = 0xcf84e0
    purple = 0xb734eb
    soft_green = 0x68c290
    soft_orange = 0xf9cb54
    soft_red = 0xcd6d6d
    yellow = 0xf9f586


class Emojis:
    star = "\u2B50"
    christmas_tree = "\U0001F384"
    check = "\u2611"
    envelope = "\U0001F4E8"
    trashcan = "<:trashcan:637136429717389331>"
    ok_hand = ":ok_hand:"

    dice_1 = "<:dice_1:755891608859443290>"
    dice_2 = "<:dice_2:755891608741740635>"
    dice_3 = "<:dice_3:755891608251138158>"
    dice_4 = "<:dice_4:755891607882039327>"
    dice_5 = "<:dice_5:755891608091885627>"
    dice_6 = "<:dice_6:755891607680843838>"

    issue = "<:IssueOpen:629695470327037963>"
    issue_closed = "<:IssueClosed:629695470570307614>"
    pull_request = "<:PROpen:629695470175780875>"
    pull_request_closed = "<:PRClosed:629695470519713818>"
    merge = "<:PRMerged:629695470570176522>"

    status_online = "<:status_online:470326272351010816>"
    status_idle = "<:status_idle:470326266625785866>"
    status_dnd = "<:status_dnd:470326272082313216>"
    status_offline = "<:status_offline:470326266537705472>"


class Hacktoberfest(NamedTuple):
    voice_id = Channels.seasonalbot_voice


class Icons:
    questionmark = "https://cdn.discordapp.com/emojis/512367613339369475.png"
    bookmark = (
        "https://images-ext-2.discordapp.net/external/zl4oDwcmxUILY7sD9ZWE2fU5R7n6QcxEmPYSE5eddbg/"
        "%3Fv%3D1/https/cdn.discordapp.com/emojis/654080405988966419.png?width=20&height=20"
    )


class Lovefest:
    role_id = int(environ.get("SEASONALBOT_LOVEFEST_ROLE_ID", 0))


class Month(enum.IntEnum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12

    def __str__(self) -> str:
        return self.name.title()


# If a month override was configured, check that it's a valid Month
# Prevents delaying an exception after the bot starts
if Client.month_override is not None:
    Month(Client.month_override)


class Roles(NamedTuple):
    admin = int(environ.get("SEASONALBOT_ADMIN_ROLE_ID", 0))
    announcements = 0
    champion = 0
    contributor = 0
    developer = 0
    devops = 0
    jammer = 0
    moderator = 0
    muted = 0
    owner = 0
    verified = 0
    helpers = 0
    rockstars = 0
    core_developers = 0


class Tokens(NamedTuple):
    giphy = environ.get("GIPHY_TOKEN")
    aoc_session_cookie = environ.get("AOC_SESSION_COOKIE")
    omdb = environ.get("OMDB_API_KEY")
    youtube = environ.get("YOUTUBE_API_KEY")
    tmdb = environ.get("TMDB_API_KEY")
    nasa = environ.get("NASA_API_KEY")
    igdb = environ.get("IGDB_API_KEY")
    github = environ.get("GITHUB_TOKEN")


class Wolfram(NamedTuple):
    user_limit_day = int(environ.get("WOLFRAM_USER_LIMIT_DAY", 10))
    guild_limit_day = int(environ.get("WOLFRAM_GUILD_LIMIT_DAY", 67))
    key = environ.get("WOLFRAM_API_KEY")


# Default role combinations
MODERATION_ROLES = Roles.moderator, Roles.admin, Roles.owner
STAFF_ROLES = Roles.helpers, Roles.moderator, Roles.admin, Roles.owner

# Whitelisted channels
WHITELISTED_CHANNELS = (
    Channels.bot,
    Channels.seasonalbot_commands,
    Channels.off_topic_0,
    Channels.off_topic_1,
    Channels.off_topic_2,
)

# Bot replies
ERROR_REPLIES = [
    "Please don't do that.",
    "You have to stop.",
    "Do you mind?",
    "In the future, don't do that.",
    "That was a mistake.",
    "You blew it.",
    "You're bad at computers.",
    "Are you trying to kill me?",
    "Noooooo!!",
    "I can't believe you've done this",
]

NEGATIVE_REPLIES = [
    "Noooooo!!",
    "Nope.",
    "I'm sorry Dave, I'm afraid I can't do that.",
    "I don't think so.",
    "Not gonna happen.",
    "Out of the question.",
    "Huh? No.",
    "Nah.",
    "Naw.",
    "Not likely.",
    "No way, José.",
    "Not in a million years.",
    "Fat chance.",
    "Certainly not.",
    "NEGATORY.",
    "Nuh-uh.",
    "Not in my house!",
]

POSITIVE_REPLIES = [
    "Yep.",
    "Absolutely!",
    "Can do!",
    "Affirmative!",
    "Yeah okay.",
    "Sure.",
    "Sure thing!",
    "You're the boss!",
    "Okay.",
    "No problem.",
    "I got you.",
    "Alright.",
    "You got it!",
    "ROGER THAT",
    "Of course!",
    "Aye aye, cap'n!",
    "I'll allow it.",
]

class Wikipedia:
    total_chance = 3
