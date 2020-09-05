import asyncio
import datetime
import logging
from typing import Optional

from discord import Color, Embed, Member
from discord.ext import commands

log = logging.getLogger(__name__)

SEARCH_API = "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={search_term}&format=json"
WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/{title}"


class WikipediaCog(commands.Cog):
    """Get info from wikipedia."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.http_session = bot.http_session

    async def search_wikipedia(self, search_term: str) -> Optional[str]:
        """Search wikipedia and return the first page found."""
        async with self.http_session.get(SEARCH_API.format(search_term=search_term)) as response:
            data = await response.json()
        page = []

        search_results = data["query"]["search"]
        if len(search_results) == 0:
            return None

        # we dont like "may refere to" pages.
        for search_result in search_results:
            if "may refer to" in search_result["snippet"]:
                pass
            else:
                page.append(search_result["title"])
        log.info("appening titles")
        return page

    @commands.command(name="wikipedia", aliases=["wiki"])
    async def w_pedia(self, ctx: commands.Context, *, search: str) -> None:
        """Gives list of item."""
        titles_no_underscore: List[str] = []
        s_desc = ''

        titles = await self.search_wikipedia(search)

        def check(user: Member) -> bool:
            return user.author.id == ctx.author.id

        if titles is None:
            await ctx.send("Sorry, we could not find a wikipedia article using that search term")
            return

        for i in titles:
            t = i.replace(" ", "_")  # wikipedia uses "_" as spaces
            final.append(t)

        async with ctx.typing():
            for index, title in enumerate(titles, start=1):
                s_desc += f'`{index}` [{title}]({WIKIPEDIA_URL.format(title=title.replace(" ", "_"))})\n'
            embed = Embed(colour=Color.blue(), title=f"Wikipedia results for `{search}`", description=s_desc)
            embed.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed=embed)

        embed = Embed(colour=Color.green(), description="Enter number to choose")
        msg = await ctx.send(embed=embed)

        try:
            user = await ctx.bot.wait_for('message', timeout=60.0, check=check)
            await ctx.send(WIKIPEDIA_URL.format(title=final[int(user.content) - 1]))

        except asyncio.TimeoutError:
            embed = Embed(colour=Color.red(), description=f"Time's up {ctx.author.mention}")
            await msg.edit(embed=embed)

        except ValueError:
            await ctx.send("I am sorry but that isn't int value")


def setup(bot: commands.Bot) -> None:
    """Uptime Cog load."""
    bot.add_cog(WikipediaCog(bot))
