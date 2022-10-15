import logging
import os
import random

from fnmatch import fnmatch

import discord
from discord.ext import commands, tasks
import anvil.server

# Setup logger.
logger = logging.getLogger(__name__)

ANVIL_UPLINK_TOKEN = os.getenv('ANVIL_UPLINK_TOKEN')


# Create bot.
class Bot(commands.Bot):
    def __init__(self):
        # Get all intents available for the bot.
        intents = discord.Intents().all()

        # Add debug guilds because registering slash commands take upwards of an hour.
        super().__init__(debug_guilds=[1012219323898679306], intents=intents)

        # Load all cogs
        self.load_cogs()

    def load_cogs(self):
        # Get all available cogs in bot/cogs directory and load them.
        cog_list = [os.path.splitext('.'.join(os.path.join(os.path.relpath(path), name).split('\\')))[0]
                    for path, sub_dirs, files in os.walk('bot\\cogs')
                    for name in files if fnmatch(name, "*.py")]

        for cog in cog_list:
            if '__init__' in cog:
                continue

            logger.info(f"Loading {cog}...")

            try:
                self.load_extension(cog)
                logger.info(f"Successfully loaded {cog}!")

            except Exception as e:
                logger.error(f"Could not load {cog}! {str(e)}")

    async def on_ready(self):
        await self.wait_until_ready()

        logger.info(f"Logged in as {self.user}!")

        await self.change_status.start()

        # anvil.server.connect(ANVIL_UPLINK_TOKEN)

    @tasks.loop(seconds=60)
    async def change_status(self):
        activities = [
            discord.Activity(
                name=f"{len(self.guilds)} servers and {sum([guild.member_count for guild in self.guilds])} users!",
                type=discord.ActivityType.watching),
            discord.Activity(name="Use /help to get started!", type=discord.ActivityType.playing)
        ]

        logger.info("Refreshing status!")

        # Change status
        await self.change_presence(
            status=discord.Status.online,
            activity=random.choice(activities),
        )
