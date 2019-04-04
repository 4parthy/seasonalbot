import json
import logging
import random
from pathlib import Path

from discord.ext import commands

log = logging.getLogger(__name__)

with open(Path('bot', 'resources', 'easter', 'starter.json'), 'r', encoding="utf8") as f:
    starters = json.load(f)


class ConvoStarters(commands.Cog):
    """A cog which posts easter conversation starters"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=('conversation_starters', 'convo_starters'))
    async def convo_starter(self, ctx):
        """Responds with a random conversation starter"""

        await ctx.send(f"{random.choice(starters['starters'])}")


def setup(bot):
    """Conversation starters Cog load."""

    bot.add_cog(ConvoStarters(bot))
    log.info("Conversation starters cog loaded")
