import asyncio
import json
import logging
import os
import pathlib
import random

import discord
from discord.ext import commands

from bot.utils.embed import format_embed

logger = logging.getLogger(__name__)


class Question(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='question', description="Provide a question to solve. Has a timeout for 15 minutes.")
    async def _question(self,
                        ctx,
                        difficulty: discord.Option(
                            str,
                            description="The difficulty of the question.",
                            choices=[
                                "easy",
                                "hard"
                            ]
                        )):
        await ctx.defer()

        # Do not allow invoking of command outside the problems channel.
        if not ctx.channel.name == 'problems':
            title = "Question: Failure!"
            description = "You cannot use this command here! Use this command in the problems channel only."

            embed = format_embed(title, description)

            await ctx.respond(embed=embed)

            return

        # Read the question status data file, or create it if it doesn't exist.
        if not pathlib.Path('bot\\data\\questions\\data.json').is_file():
            data = {}

            for team_name in ctx.guild.categories:
                data[team_name.name] = {'current_question': '',
                                        'solved_questions': []}

            with open('bot\\data\\questions\\data.json', 'w+') as data_file:
                json.dump(data, data_file)
                data_file.close()

        else:
            with open('bot\\data\\questions\\data.json', 'r') as data_file:
                data = json.load(data_file)
                data_file.close()

        # Get the team name from channel category.
        team_name = ctx.channel.category.name

        # If the team skipped a question, add it to solved_questions and clear the current question.
        if data[team_name]['current_question'] != '':
            data[team_name]['solved_questions'].append(data[team_name]['current_question'])
            data[team_name]['current_question'] = ''

        # Store all available questions into a dictionary, sorting by difficulty.
        questions_list = {
            "easy": [os.path.join(os.path.relpath(path), name) for path, sub_dirs, files in
                     os.walk('bot\\data\\questions\\easy') for name in files],
            "hard": [os.path.join(os.path.relpath(path), name) for path, sub_dirs, files in
                     os.walk('bot\\data\\questions\\hard') for name in files],
        }

        # Get the path of the randomly chosen question from questions_list.
        question_path = random.choice(
            [question for question in questions_list[difficulty]
             if question not in data[team_name]['solved_questions']])
        question_name = '-'.join(question_path.split('\\')[-1].split('.')[0].split(' ')).lower()

        # Store the random question as the current question and write to data file.
        data[team_name]['current_question'] = question_name

        with open('bot\\data\\questions\\data.json', 'w') as data_file:
            json.dump(data, data_file)
            data_file.close()

        # Create and add question muted role to the user.
        await ctx.guild.create_role(name=f"{team_name} {question_name}")

        role = discord.utils.get(ctx.guild.roles, name=f"{team_name} {question_name}")

        await ctx.channel.set_permissions(role, read_messages=True, send_messages=False)
        await ctx.user.add_roles(role)

        # Send the question pdf as an attachment.
        file = discord.File(question_path)
        await ctx.respond(file=file)

        logger.info(f"Sent {question_name} to {team_name}!")

        # Sleep for 15 minutes.
        await asyncio.sleep(900)

        # Send the timeout removal message if the timeout is still present.
        try:
            title = "Question: Success!"
            description = "Your timeout of 15 minutes has passed! You can request for a new question now."

            embed = format_embed(title, description)

            await ctx.send(embed=embed)
            await role.delete()

        # If the role doesn't exist (it was deleted after submission), don't do anything.
        except commands.RoleNotFound:
            pass


def setup(bot):
    bot.add_cog(Question(bot))
