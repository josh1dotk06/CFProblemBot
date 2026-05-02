from typing import Optional

import discord #import discord library in here
from discord import app_commands
from discord.ext import commands

class BasicCommands(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check if the bot is online.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong! The bot is online")




    @app_commands.command(name="connect", description="Connect your Codeforces handle.")
    @app_commands.describe(codeforces_handle="Your Codeforces username/handle.")
    async def connect(self, interaction: discord.Interaction, codeforces_handle: str):
        await interaction.response.send_message(f"Placeholder: connected Discord user `{interaction.user}` to Codeforces handle `{codeforces_handle}`.")
        #continue stuff here or something 



    @app_commands.command(name="generate", description="Generate Codeforces problem recommendations.")
    @app_commands.describe(
        unseen="Only recommend problems you have not solved yet.",
        min_rating="Minimum Codeforces problem rating.",
        max_rating="Maximum Codeforces problem rating.",
        include_tags="Comma separated tags to include, like greedy,binary search.",
        exclude_tags="Comma separated tags to exclude, like dp,math.",
        exact_match="Only allow problems with exactly the included tags.",
        count="Number of problems to generate."
    )

    async def generate(
        self,
        interaction: discord.Interaction,
        unseen: bool = False,
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None,
        include_tags: Optional[str] = None,
        exclude_tags: Optional[str] = None,
        exact_match: bool = False,
        count: app_commands.Range[int, 1, 10] = 1
    ):
        await interaction.response.send_message(
            "Placeholder generate command received.\n"
            f"unseen: `{unseen}`\n"
            f"min_rating: `{min_rating}`\n"
            f"max_rating: `{max_rating}`\n"
            f"include_tags: `{include_tags}`\n"
            f"exclude_tags: `{exclude_tags}`\n"
            f"exact_match: `{exact_match}`\n"
            f"count: `{count}`"
        )
        #continue stuff, just testing yknow


async def setup(bot: commands.Bot):
    await bot.add_cog(BasicCommands(bot)) #add cog BasicCommands to bot

