import logging
import os

from bot.bot import Bot
from dotenv import load_dotenv
from rich.logging import RichHandler

load_dotenv()

# Get discord token
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Setup logging using rich's logging handler.
FORMAT = "%(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)],
)

logger = logging.getLogger()


def main(token):
    bot = Bot()

    # Run the bot.
    bot.run(token)


if __name__ == "__main__":
    main(DISCORD_TOKEN)
