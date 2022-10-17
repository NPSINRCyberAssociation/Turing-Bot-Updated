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

anvil.server.connect(ANVIL_CLIENT_KEY)


class Scoring(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    scoring = discord.SlashCommandGroup("scoring", "Scoring related commands.")

    @scoring.command(
        name="easy", description="Add a point to the team that solved an easy question."
    )
    @commands.has_permissions(administrator=True)
    async def _easy(
            self,
            ctx,
            team_name: discord.Option(
                str,
                description="The team to add a point to.",
                choices=[
                    team
                    for team, value in json.load(
                        open("bot\\data\\questions\\data.json", "r")
                    ).items()
                ],
            ),
    ):
        await ctx.defer()

        anvil.server.call("solve_easy", team_name)

        title = "Scoring - Easy: Success!"
        description = f"Updated the score of {team_name} for solving an easy question!"

        embed = format_embed(title, description)
        await ctx.respond(embed=embed)

    @_easy.error
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            title = "Scoring - Easy: Error!"
            description = (
                f"Unable to score: The user has insufficient permissions to score!"
            )

            embed = format_embed(title, description)
            await ctx.respond(embed=embed)

    @scoring.command(
        name="hard", description="Transfer points between teams as per the teams wish."
    )
    @commands.has_permissions(administrator=True)
    async def _hard(
            self,
            ctx,
            team_name_1: discord.Option(
                str,
                description="The team to add a point to.",
                choices=[
                    team
                    for team, value in json.load(
                        open("bot\\data\\questions\\data.json", "r")
                    ).items()
                ],
            ),
            team_name_2: discord.Option(
                str,
                description="The team to subtract a point from.",
                choices=[
                    team
                    for team, value in json.load(
                        open("bot\\data\\questions\\data.json", "r")
                    ).items()
                ],
            ),
    ):
        await ctx.defer()

        anvil.server.call("solve_hard", team_name_1, team_name_2)

        title = "Scoring - Hard: Success!"
        description = f"Updated the scores of {team_name_1} and {team_name_2} for solving a hard question!"

        embed = format_embed(title, description)
        await ctx.respond(embed=embed)

    @_hard.error
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            title = "Scoring - Hard: Error!"
            description = (
                f"Unable to score: The user has insufficient permissions to score!"
            )

            embed = format_embed(title, description)
            await ctx.respond(embed=embed)

    @scoring.command(name="set", description="Manually set the score of a team.")
    @commands.has_permissions(administrator=True)
    async def _set(
            self,
            ctx,
            team_name: discord.Option(
                str,
                description="The team to set the score.",
                choices=[
                    team
                    for team, value in json.load(
                        open("bot\\data\\questions\\data.json", "r")
                    ).items()
                ],
            ),
            score: discord.Option(int, description="The score to set."),
    ):
        await ctx.defer()

        anvil.server.call("set_score", team_name, score)

        title = "Scoring - Set: Success!"
        description = f"Set the score of {team_name} to {score}!"

        embed = format_embed(title, description)
        await ctx.respond(embed=embed)

    @_easy.error
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            title = "Scoring - Set: Error!"
            description = (
                f"Unable to score: The user has insufficient permissions to score!"
            )

            embed = format_embed(title, description)
            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Scoring(bot))
