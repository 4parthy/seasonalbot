import logging
import random
from datetime import datetime
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from discord import Embed
from discord.ext.commands import Cog, Context, group

from bot.bot import SeasonalBot
from bot.constants import Tokens

logger = logging.getLogger(__name__)

NASA_BASE_URL = "https://api.nasa.gov"
NASA_IMAGES_BASE_URL = "https://images-api.nasa.gov"
NASA_EPIC_BASE_URL = "https://epic.gsfc.nasa.gov"

APOD_DEFAULT_PARAMS = {
    "api_key": Tokens.nasa
}


class Space(Cog):
    """Space Cog contains commands, that show images, facts or other information about space."""

    def __init__(self, bot: SeasonalBot):
        self.bot = bot
        self.http_session = bot.http_session

    @group(name="space")
    async def space(self, ctx: Context) -> None:
        """Head command that contains commands about space."""
        await ctx.send_help("space")

    @space.command(name="apod")
    async def apod(self, ctx: Context, date: Optional[str] = None) -> None:
        """Get Astronomy Picture of Day from NASA API. Date is optional parameter, what formatting is YYYY-MM-DD."""
        # Make copy of parameters
        params = APOD_DEFAULT_PARAMS.copy()
        # Parse date to params, when provided. Show error message when invalid formatting
        if date:
            try:
                params["date"] = datetime.strptime(date, "%Y-%m-%d").date().isoformat()
            except ValueError:
                await ctx.send(f"Invalid date {date}. Please make sure your date is in format YYYY-MM-DD.")
                return

        # Do request to NASA API
        result = await self.fetch_from_nasa("planetary/apod", params)

        # Create embed from result
        embed = Embed(title=f"Astronomy Picture of the Day - {result['date']}", description=result["explanation"])
        embed.set_image(url=result["url"])
        embed.set_footer(text="Powered by NASA API")

        await ctx.send(embed=embed)

    @space.command(name="nasa")
    async def nasa(self, ctx: Context) -> None:
        """Get random NASA information/facts + image."""
        page = random.randint(1, 50)

        # Create params for request, create URL and do request
        params = {
            "media_type": "image",
            "page": page
        }
        async with self.http_session.get(url=f"{NASA_IMAGES_BASE_URL}/search?{urlencode(params)}") as resp:
            data = await resp.json()

        # Get (random) item from result, that will be shown
        item = random.choice(data["collection"]["items"])

        # Create embed and send it
        embed = Embed(title=item["data"][0]["title"], description=item["data"][0]["description"])
        embed.set_image(url=item["links"][0]["href"])
        embed.set_footer(text="Powered by NASA API")

        await ctx.send(embed=embed)

    @space.command(name="epic")
    async def epic(self, ctx: Context) -> None:
        """Get one of latest random image of earth from NASA EPIC API."""
        # Generate URL and make request to API
        async with self.http_session.get(url=f"{NASA_EPIC_BASE_URL}/api/natural") as resp:
            data = await resp.json()

        # Get random item from result that will be shown
        item = random.choice(data)

        # Split date for image URL
        year, month, day = item["date"].split(" ")[0].split("-")

        image_url = f"{NASA_EPIC_BASE_URL}/archive/natural/{year}/{month}/{day}/jpg/{item['image']}.jpg"

        # Create embed, fill and send it
        embed = Embed(title="Earth Image", description=item["caption"])
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Identifier: {item['identifier']} \u2022 Powered by NASA API")

        await ctx.send(embed=embed)

    @space.command(name="mars")
    async def mars(self, ctx: Context, date: str) -> None:
        """
        Get random Mars image by date.

        Date formatting is YYYY-MM-DD. Current max date is 2019-09-28 and min 2012-08-06.
        """
        # Create API request parameters, try to parse date
        params = {
            "api_key": Tokens.nasa
        }
        try:
            params["earth_date"] = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            await ctx.send(f"Invalid date {date}. Please make sure your date is in format YYYY-MM-DD.")
            return

        result = await self.fetch_from_nasa("mars-photos/api/v1/rovers/curiosity/photos", params)

        # Check for empty result
        if len(result["photos"]) < 1:
            err_msg = (
                f"We can't find result in date {date}. "
                "**Note:** Current dates must in range 2012-08-06 and 2019-09-28."
            )
            await ctx.send(err_msg)
            return

        # Get random item from result, generate embed with it and send
        item = random.choice(result["photos"])

        embed = Embed(title=f"{item['rover']['name']}'s {item['camera']['full_name']} Mars Image")
        embed.set_image(url=item["img_src"])
        embed.set_footer(text="Powered by NASA API")

        await ctx.send(embed=embed)

    async def fetch_from_nasa(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch information from NASA API, return result."""
        # Generate request URL from base URL, endpoint and parsed params
        async with self.http_session.get(url=f"{NASA_BASE_URL}/{endpoint}?{urlencode(params)}") as resp:
            return await resp.json()


def setup(bot: SeasonalBot) -> None:
    """Load Space Cog."""
    # Check does bot have NASA API key in .env, when not, don't load Cog and print warning
    if not Tokens.nasa:
        logger.warning("Can't find NASA API key. Not loading Space Cog.")
        return

    bot.add_cog(Space(bot))
