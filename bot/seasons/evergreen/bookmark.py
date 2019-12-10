import logging
import random

import discord
from discord.ext import commands

from bot.constants import Colours, ERROR_REPLIES, Emojis

log = logging.getLogger(__name__)


class Bookmark(commands.Cog):
    """Creates personal bookmarks by relaying a message link to the user's DMs."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="bookmark", aliases=("bm", "pin"))
    async def bookmark(
        self,
        ctx: commands.Context,
        target_message: discord.Message,
        *,
        title: str = "Bookmark"
    ) -> None:
        """Send the author a link to `target_message` via DMs."""
        log.info(f"{ctx.author} bookmarked {target_message.jump_url} with title '{title}'")
        embed = discord.Embed(
            title=title,
            colour=Colours.soft_green,
            description=(
                f"{target_message.content}\n\n"
                f"[Visit original message]({target_message.jump_url})"
            )
        )
        embed.set_author(name=target_message.author, icon_url=target_message.author.avatar_url)
        embed.set_thumbnail(url="https://img.icons8.com/color/48/FF3333/bookmark-ribbon.png")

        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            error_embed = discord.Embed(
                title=random.choice(ERROR_REPLIES),
                description=f"{ctx.author.mention}, please enable your DMs to receive the bookmark",
                colour=Colours.soft_red
            )
            await ctx.send(embed=error_embed)
        else:
            await ctx.message.add_reaction(Emojis.envelope)


def setup(bot: commands.Bot) -> None:
    """Load the Bookmark cog."""
    bot.add_cog(Bookmark(bot))
    log.info("Bookmark cog loaded")
