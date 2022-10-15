import json
import logging
import os

import anvil.server
import discord
from bot.utils.embed import format_embed
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

ANVIL_CLIENT_KEY = os.getenv("ANVIL_CLIENT_KEY")


class Scoring(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    scoring = discord.SlashCommandGroup("scoring", "Scoring related commands.")

    @scoring.command(
        name="easy", description="Add a point to the team that solved an easy question."
    )
    async def _easy(
        self,
        ctx,
        team_name: discord.Option(
            str,
            description="The team to add a point to.",
            choices=[
                team
                for team, value in json.load(
                    open("bot/data/questions/data.json", "r")
                ).items()
            ],
        ),
    ):
        await ctx.defer()

        anvil.server.call("solve_easy", team_name)

        title = "Scoring - Easy: Success!"
        description = "Updated the score of {team_name} for solving an easy question!"

        embed = format_embed(title, description)
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Scoring(bot))
