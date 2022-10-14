import json
import logging

import discord
from discord.ext import commands

import anvil

logger = logging.getLogger(__name__)


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



def setup(bot):
    bot.add_cog(Scoring(bot))
