import contextlib
import datetime
import importlib
import inspect
import logging
import pkgutil
from pathlib import Path
from typing import List, Optional, Tuple, Type, Union

import discord
from discord.ext import commands

from bot.bot import bot
from bot.constants import Channels, Client, Roles
from bot.decorators import with_role

log = logging.getLogger(__name__)

ICON_BASE_URL = "https://raw.githubusercontent.com/python-discord/branding/master"


def get_seasons() -> List[str]:
    """Returns all the Season objects located in /bot/seasons/."""
    seasons = []

    for module in pkgutil.iter_modules([Path("bot/seasons")]):
        if module.ispkg:
            seasons.append(module.name)
    return seasons


def get_season_class(season_name: str) -> Type["SeasonBase"]:
    """Gets the season class of the season module."""
    season_lib = importlib.import_module(f"bot.seasons.{season_name}")
    class_name = season_name.replace("_", " ").title().replace(" ", "")
    return getattr(season_lib, class_name)


def get_season(season_name: str = None, date: datetime.datetime = None) -> "SeasonBase":
    """Returns a Season object based on either a string or a date."""
    # If either both or neither are set, raise an error.
    if not bool(season_name) ^ bool(date):
        raise UserWarning("This function requires either a season or a date in order to run.")

    seasons = get_seasons()

    # Use season override if season name not provided
    if not season_name and Client.season_override:
        log.debug(f"Season override found: {Client.season_override}")
        season_name = Client.season_override

    # If name provided grab the specified class or fallback to evergreen.
    if season_name:
        season_name = season_name.lower()
        if season_name not in seasons:
            season_name = "evergreen"
        season_class = get_season_class(season_name)
        return season_class()

    # If not, we have to figure out if the date matches any of the seasons.
    seasons.remove("evergreen")
    for season_name in seasons:
        season_class = get_season_class(season_name)
        # check if date matches before returning an instance
        if season_class.is_between_dates(date):
            return season_class()
    else:
        evergreen_class = get_season_class("evergreen")
        return evergreen_class()


class SeasonBase:
    """Base class for Seasonal classes."""

    name: Optional[str] = "evergreen"
    bot_name: str = "SeasonalBot"

    start_date: Optional[str] = None
    end_date: Optional[str] = None
    should_announce: bool = False

    colour: Optional[int] = None
    icon: Tuple[str, ...] = ("/logos/logo_full/logo_full.png",)
    bot_icon: Optional[str] = None

    date_format: str = "%d/%m/%Y"

    index: int = 0

    @staticmethod
    def current_year() -> int:
        """Returns the current year."""
        return datetime.date.today().year

    @classmethod
    def start(cls) -> datetime.datetime:
        """
        Returns the start date using current year and start_date attribute.

        If no start_date was defined, returns the minimum datetime to ensure it's always below checked dates.
        """
        if not cls.start_date:
            return datetime.datetime.min
        return datetime.datetime.strptime(f"{cls.start_date}/{cls.current_year()}", cls.date_format)

    @classmethod
    def end(cls) -> datetime.datetime:
        """
        Returns the start date using current year and end_date attribute.

        If no end_date was defined, returns the minimum datetime to ensure it's always above checked dates.
        """
        if not cls.end_date:
            return datetime.datetime.max
        return datetime.datetime.strptime(f"{cls.end_date}/{cls.current_year()}", cls.date_format)

    @classmethod
    def is_between_dates(cls, date: datetime.datetime) -> bool:
        """Determines if the given date falls between the season's date range."""
        return cls.start() <= date <= cls.end()

    @property
    def name_clean(self) -> str:
        """Return the Season's name with underscores replaced by whitespace."""
        return self.name.replace("_", " ").title()

    @property
    def greeting(self) -> str:
        """
        Provides a default greeting based on the season name if one wasn't defined in the season class.

        It's recommended to define one in most cases by overwriting this as a normal attribute in the
        inheriting class.
        """
        return f"New Season, {self.name_clean}!"

    async def apply_username(self, *, debug: bool = False) -> Union[bool, None]:
        """
        Applies the username for the current season.

        Only changes nickname if `bool` is False, otherwise only changes the nickname.

        Returns True if it successfully changed the username.
        Returns False if it failed to change the username, falling back to nick.
        Returns None if `debug` was True and username change wasn't attempted.
        """
        guild = bot.get_guild(Client.guild)
        result = None

        # Change only nickname if in debug mode due to ratelimits for user edits
        if debug:
            if guild.me.display_name != self.bot_name:
                log.debug(f"Changing nickname to {self.bot_name}")
                await guild.me.edit(nick=self.bot_name)

        else:
            if bot.user.name != self.bot_name:
                # Attempt to change user details
                log.debug(f"Changing username to {self.bot_name}")
                with contextlib.suppress(discord.HTTPException):
                    await bot.user.edit(username=self.bot_name)

                # Fallback on nickname if failed due to ratelimit
                if bot.user.name != self.bot_name:
                    log.warning(f"Username failed to change: Changing nickname to {self.bot_name}")
                    await guild.me.edit(nick=self.bot_name)
                    result = False
                else:
                    result = True

            # Remove nickname if an old one exists
            if guild.me.nick and guild.me.nick != self.bot_name:
                log.debug(f"Clearing old nickname of {guild.me.nick}")
                await guild.me.edit(nick=None)

            return result

    async def announce_season(self) -> None:
        """
        Announces a change in season in the announcement channel.

        Auto-announcement is configured by the `should_announce` `SeasonBase` attribute
        """
        # Short circuit if the season had disabled automatic announcements
        if not self.should_announce:
            log.debug(f"Season changed without announcement: {self.name}")
            return

        guild = bot.get_guild(Client.guild)
        channel = guild.get_channel(Channels.announcements)
        mention = f"<@&{Roles.announcements}>"

        # Build cog info output
        doc = inspect.getdoc(self)
        announce = "\n\n".join(l.replace("\n", " ") for l in doc.split("\n\n"))

        # No announcement message found
        if not doc:
            return

        embed = discord.Embed(description=f"{announce}\n\n", colour=self.colour or guild.me.colour)
        embed.set_author(name=self.greeting)

        if self.icon:
            embed.set_image(url=ICON_BASE_URL+self.icon[0])

        # Find any seasonal commands
        cogs = []
        for cog in bot.cogs.values():
            if "evergreen" in cog.__module__:
                continue
            cog_name = type(cog).__name__
            if cog_name != "SeasonManager":
                cogs.append(cog_name)

        if cogs:
            def cog_name(cog: commands.Cog) -> str:
                return type(cog).__name__

            cog_info = []
            for cog in sorted(cogs, key=cog_name):
                doc = inspect.getdoc(bot.get_cog(cog))
                if doc:
                    cog_info.append(f"**{cog}**\n*{doc}*")
                else:
                    cog_info.append(f"**{cog}**")

            cogs_text = "\n".join(cog_info)
            embed.add_field(name="New Command Categories", value=cogs_text)
            embed.set_footer(text="To see the new commands, use .help Category")

        await channel.send(mention, embed=embed)

    async def load(self) -> None:
        """
        Loads extensions, bot name and avatar, server icon and announces new season.

        If in debug mode, the avatar, server icon, and announcement will be skipped.
        """
        self.index = 0
        # Prepare all the seasonal cogs, and then the evergreen ones.
        extensions = []
        for ext_folder in {self.name, "evergreen"}:
            if ext_folder:
                log.info(f"Start loading extensions from seasons/{ext_folder}/")
                path = Path("bot/seasons") / ext_folder
                for ext_name in [i[1] for i in pkgutil.iter_modules([path])]:
                    extensions.append(f"bot.seasons.{ext_folder}.{ext_name}")

        # Finally we can load all the cogs we've prepared.
        bot.load_extensions(extensions)

        # Apply seasonal elements after extensions successfully load
        username_changed = await self.apply_username(debug=Client.debug)

        # Avoid major changes and announcements if debug mode
        if not Client.debug:
            log.info("Applying avatar.")
            await self.apply_avatar()
            if username_changed:
                log.info("Applying server icon.")
                await self.apply_server_icon()
                log.info(f"Announcing season {self.name}.")
                await self.announce_season()
            else:
                log.info(f"Skipping server icon change due to username not being changed.")
                log.info(f"Skipping season announcement due to username not being changed.")

        await bot.send_log("SeasonalBot Loaded!", f"Active Season: **{self.name_clean}**")


class SeasonManager(commands.Cog):
    """A cog for managing seasons."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        season_class = get_season_class("evergreen")
        self.season = season_class()
        self.season_task = bot.loop.create_task(self.season.load())

    @with_role(Roles.moderator, Roles.admin, Roles.owner)
    @commands.command(name="season")
    async def change_season(self, ctx: commands.Context, new_season: str) -> None:
        """Changes the currently active season on the bot."""
        self.season = get_season(season_name=new_season)
        await self.season.load()
        await ctx.send(f"Season changed to {new_season}.")

    @with_role(Roles.moderator, Roles.admin, Roles.owner)
    @commands.command(name="seasons")
    async def show_seasons(self, ctx: commands.Context) -> None:
        """Shows the available seasons and their dates."""
        # Sort by start order, followed by lower duration
        def season_key(season_class: Type[SeasonBase]) -> Tuple[datetime.datetime, datetime.timedelta]:
            return season_class.start(), season_class.end() - datetime.datetime.max

        current_season = self.season.name

        forced_space = "\u200b "

        entries = []
        seasons = [get_season_class(s) for s in get_seasons()]
        for season in sorted(seasons, key=season_key):
            start = season.start_date
            end = season.end_date
            if start and not end:
                period = f"From {start}"
            elif end and not start:
                period = f"Until {end}"
            elif not end and not start:
                period = f"Always"
            else:
                period = f"{start} to {end}"

            # Bold period if current date matches season date range
            is_current = season.is_between_dates(datetime.datetime.utcnow())
            pdec = "**" if is_current else ""

            # Underline currently active season
            is_active = current_season == season.name
            sdec = "__" if is_active else ""

            entries.append(
                f"**{sdec}{season.__name__}:{sdec}**\n"
                f"{forced_space*3}{pdec}{period}{pdec}\n"
            )

        embed = discord.Embed(description="\n".join(entries), colour=ctx.guild.me.colour)
        embed.set_author(name="Seasons")
        await ctx.send(embed=embed)

    @with_role(Roles.moderator, Roles.admin, Roles.owner)
    @commands.group()
    async def set(self, ctx: commands.Context) -> None:
        """Change aspects of the bot or server."""
        if not ctx.invoked_subcommand:
            await ctx.send_help(ctx.command)

    @set.command(name="avatar", aliases=["avy"])
    async def set_avatar(self, ctx: commands.Context, *, image_url: str = None) -> None:
        """Sets the bot avatar."""
        if not image_url:
            image_url = f"{ICON_BASE_URL}/logos/logo_seasonal/evergreen/logo_evergreen.png"
        elif image_url.startswith("<"):
            image_url = image_url.strip("<>")

        is_changed = await ctx.bot.set_avatar(image_url)

        embed = discord.Embed(
            title="Avatar changed." if is_changed else "Avatar change failed.",
            colour=discord.Colour.green() if is_changed else discord.Colour.red()
        )
        await ctx.send(embed=embed)

    @set.command(name="icon")
    async def set_server_icon(self, ctx: commands.Context, *, image_url: str = None) -> None:
        """Sets the server icon."""
        if not image_url:
            image_url = f"{ICON_BASE_URL}/logos/logo_full/logo_full.png"
        elif image_url.startswith("<"):
            image_url = image_url.strip("<>")

        is_changed = await ctx.bot.set_icon(image_url)

        embed = discord.Embed(
            title="Server icon changed." if is_changed else "Server icon change failed.",
            colour=discord.Colour.green() if is_changed else discord.Colour.red()
        )
        await ctx.send(embed=embed)

    @set.command(name="username", aliases=["name"])
    async def set_username(self, ctx: commands.Context, *, new_name: str = None) -> None:
        """Sets the bot username."""
        new_name = new_name or "SeasonalBot"
        is_changed = await ctx.bot.set_username(new_name)

        if is_changed:
            title = f"Username changed to {new_name}"
        else:
            if is_changed is False:
                title = f"Username change failed, Nickname changed to {new_name} instead."
            else:
                title = "Username change failed."

        embed = discord.Embed(
            colour=discord.Colour.green() if is_changed else discord.Colour.red(),
            title=title
        )
        await ctx.send(embed=embed)

    @set.command(name="nickname", aliases=["nick"])
    async def set_nickname(self, ctx: commands.Context, *, new_name: str = None) -> None:
        """Sets the bot nickname."""
        new_name = new_name or "SeasonalBot"
        is_changed = await ctx.bot.set_nickname(new_name)

        embed = discord.Embed(
            colour=discord.Colour.green() if is_changed else discord.Colour.red(),
            title=f"Nickname changed to {new_name}" if is_changed else "Nickname change failed."
        )
        await ctx.send(embed=embed)
