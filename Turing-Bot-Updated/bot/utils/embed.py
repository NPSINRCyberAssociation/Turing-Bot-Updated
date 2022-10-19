import datetime

import discord


def format_embed(title, description, color=discord.Color.from_rgb(0, 0, 0), image=None):
    embed = discord.Embed(
        title=title, description=description, color=color
    )

    if image is not None:
        embed.set_image(url=image)

    return embed
