import logging
import random

import discord
from discord.ext import commands

from bot.constants import ERROR_REPLIES, Colours

log = logging.getLogger(__name__)


class Bookmark(commands.Cog):
    """A cog that creates personal bookmarks by relaying a message to the user's DMs."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="bookmark", aliases=("bm", "pin"))
    async def bookmark(self, ctx: commands.Context, jump_url: str = None, *args) -> None:
        """Bookmarks a message."""
        if jump_url is not None and jump_url != "*":
            if "discordapp.com/channels" not in jump_url:
                embed_error_1 = discord.Embed(
                    title=random.choice(ERROR_REPLIES),
                    description="I can't find the associated message. "
                                "This command supports the following syntax:\n"
                                "`[command alias] [message url] (bookmark name)`",
                    colour=Colours.soft_red
                )
                await ctx.send(embed=embed_error_1)
                return
        if jump_url is None or jump_url == "*":
            channel = ctx.channel
            async for message in channel.history(limit=2):
                jump_url = message.jump_url

        embed = discord.Embed(
            title="Your bookmark",
            description=None,
            colour=Colours.soft_green
        )
        hint = ' '.join(args)
    
        if hint == "":
            hint = "No hint provided."

        embed.set_footer(text="Why everything so heavy ?")
        embed.set_thumbnail(
            url="https://emojipedia-us.s3."
                "dualstack.us-west-1.amazonaws.com"
                "/thumbs/240/twitter/"
                "233/incoming-envelope_1f4e8.png"
        )
        embed.set_author(name=ctx.author)
        embed.add_field(name='Hints', value=hint, inline=False)
        embed.add_field(name='Link', value=jump_url, inline=False)
        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            embed_error_2 = discord.Embed(
                title=random.choice(ERROR_REPLIES),
                description="You have to enable direct messages from this server to receive DM's from me.",
                colour=Colours.soft_red
            )
            await ctx.send(embed=embed_error_2)
            return
        await ctx.send("Sent you a DM!")


def setup(bot: commands.Bot) -> None:
    """Bookmark Cog load."""
    bot.add_cog(Bookmark(bot))
    log.info("Bookmark cog loaded")
