import json
import logging
import pathlib

import discord
from discord.ext import commands

from bot.utils.embed import format_embed

logger = logging.getLogger(__name__)


class ScorerModal(discord.ui.Modal):
    def __init__(self, answer, channel, *args, **kwargs):
        super().__init__(*args, **kwargs, title="Enter your custom response.")

        self.answer = answer
        self.channel = channel

        self.add_item(discord.ui.InputText(label="Custom response: ", style=discord.InputTextStyle.long))

    async def callback(self, interaction):
        title = "Submit"
        description = f"Your answer was {self.answer}!" \
                      f"\n{self.children[0]}"

        embed = format_embed(title, description)

        await self.channel.send(embed=embed)


class ScorerButtons(discord.ui.View):
    def __init__(self, channel, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.channel = channel

    @discord.ui.button(label="Correct!", style=discord.ButtonStyle.green)
    async def correct_button_callback(self, button, interaction):
        await interaction.response.send_modal(ScorerModal(answer='correct', channel=self.channel))

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Incorrect!", style=discord.ButtonStyle.danger)
    async def incorrect_button_callback(self, button, interaction):
        await interaction.response.send_modal(ScorerModal(answer='incorrect', channel=self.channel))

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(view=self)


class AnswerModal(discord.ui.Modal):
    def __init__(self, question_name, *args, **kwargs):
        super().__init__(*args, **kwargs, title=f"Submit your answer for {question_name}.")

        self.question_name = question_name

        self.add_item(discord.ui.InputText(label="Answer: ", style=discord.InputTextStyle.long))

    async def callback(self, interaction):
        title = "Submit: Success!"
        description = f"Team: {interaction.channel.category.name}" \
                      f"\nQuestion: {self.question_name}" \
                      f"\nAnswer: {self.children[0]}"

        embed = format_embed(title, description)

        # Get the submissions channel where all submissions will go.
        submissions_channel = discord.utils.get(interaction.guild.channels, name='submissions')

        await submissions_channel.send(embed=embed, view=ScorerButtons(channel=interaction.channel))


class Submit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='submit', description="Submit your answer for the current problem.")
    async def _submit(self, ctx):
        await ctx.defer()

        # Do not allow invoking of command outside the submit channel.
        if not ctx.channel.name == 'submit':
            title = "Submit: Failure!"
            description = "You cannot use this command here! Use this command in the submit channel only."

            embed = format_embed(title, description)

            await ctx.respond(embed=embed)

        # Read the question status data file, or create it if it doesn't exist.
        if not pathlib.Path('bot/data/questions/data.json').is_file():
            data = {}

            for team_name in ctx.guild.categories:
                data[team_name] = {'current_question': '',
                                   'solved_questions': []}

            with open('bot/data/questions/data.json', 'w+') as data_file:
                json.dump(data, data_file)
                data_file.close()

        else:
            with open('bot/data/questions/data.json', 'r') as data_file:
                data = json.load(data_file)
                data_file.close()

        # Get the team name from channel category.
        team_name = ctx.channel.category.name

        # Get the current question.
        question_name = data[team_name]['current_question']

        # If there is no current question, prompt to generate a new question.
        if question_name == '':
            title = "Submit: Error!"
            description = "There is no available question to answer! Generate a new question using the /question " \
                          "command in the problems channel "

            embed = format_embed(title, description)
            await ctx.respond(embed=embed)

            return

        # Create a modal for answering the question.
        await ctx.send_modal(AnswerModal(question_name=question_name))

        title = "Submit: Success!"
        description = f"Your answer for {question_name} has been sent to a scorer!" \
                      " It will be evaluated and scored shortly."

        embed = format_embed(title, description)
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Submit(bot))
