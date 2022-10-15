import json
import logging
import os

import discord
from discord.ext import commands

from dotenv import load_dotenv

import anvil.server

load_dotenv()

logger = logging.getLogger(__name__)

ANVIL_UPLINK_TOKEN = os.getenv('ANVIL_CLIENT_KEY')


class Scoring(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    scoring = discord.SlashCommandGroup("scoring", "Scoring related commands.")

    @scoring.command(name='easy', description="Add a point to the team that solved an easy question.")
    async def _easy(self,
                    ctx,
                    team_name: discord.Option(
                        str,
                        description="The team to add a point to.",
                        choices=[team for team, value in
                                 json.load(open('bot\\data\\questions\\data.json', 'r')).items()]
                    )):
        await ctx.defer()

        logger.info(ANVIL_UPLINK_TOKEN)
        logger.info("Hello")
        anvil.server.connect(ANVIL_UPLINK_TOKEN)
        anvil.server.call('solve_easy', team_name)


def setup(bot):
    bot.add_cog(Scoring(bot))
