from typing import Optional

import discord #import discord library in here
from discord import app_commands
from discord.ext import commands

#import our custom stuff from client and user_store
from codeforces.client import get_user_info, CodeforcesAPIError, get_problemset
from storage.user_store import connect_user

#generating random problem
import random 

from recommender.filters import (filter_by_rating, filter_by_include_tags, filter_by_exclude_tags, parse_tags, filter_by_exact_tags)

class BasicCommands(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check if the bot is online.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong! The bot is online")



    #modifying this on second iteration
    @app_commands.command(name="connect", description="Connect your Codeforces handle.")
    @app_commands.describe(codeforces_handle="Your Codeforces username/handle.")
    async def connect(self, interaction: discord.Interaction, codeforces_handle: str):
        #await interaction.response.send_message(f"Placeholder: connected Discord user `{interaction.user}` to Codeforces handle `{codeforces_handle}`.")
        #continue stuff here or something 

        await interaction.response.defer()

        try:
            #get cf data
            user_info = await get_user_info(codeforces_handle)
        except CodeforcesAPIError as error:
            await interaction.followup.send(f"Could not connect that handle: `{error}`")
            return

        #"handle":"tourist" eg
        confirmed_handle = user_info["handle"]
        discord_id = interaction.user.id

        #connect (load into JSON)
        connect_user(discord_id, confirmed_handle)
        await interaction.followup.send(f"Successfully connected your Discord account to Codeforces handle `{confirmed_handle}`.")

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
        # await interaction.response.send_message(
        #     "Placeholder generate command received.\n"
        #     f"unseen: `{unseen}`\n"
        #     f"min_rating: `{min_rating}`\n"
        #     f"max_rating: `{max_rating}`\n"
        #     f"include_tags: `{include_tags}`\n"
        #     f"exclude_tags: `{exclude_tags}`\n"
        #     f"exact_match: `{exact_match}`\n"
        #     f"count: `{count}`"
        # )
        #continue stuff, just testing yknow

        await interaction.response.defer()

        problemset = await get_problemset()
        #only consider the actual problems right now (not problemStatistics)
        problemset = problemset["problems"]

        #testing the 4 basic filters first
        include_tag_list = parse_tags(include_tags)
        exclude_tag_list = parse_tags(exclude_tags)
        problemset = filter_by_rating(problemset, min_rating, max_rating)
        problemset = filter_by_include_tags(problemset, include_tag_list)

        if exact_match == True:
            problemset = filter_by_exact_tags(problemset, include_tag_list)
        else:
            problemset = filter_by_exclude_tags(problemset, exclude_tag_list)

        randVar = random.randint(0, len(problemset) - 1)
        problem = problemset[randVar]
        print(problem)

        name = problem.get("name")
        contest_id = problem.get("contestId")
        index = problem.get("index")
        rating = problem.get("rating")
        tags = problem.get("tags")
        problem_url = f"https://codeforces.com/problemset/problem/{contest_id}/{index}"


        await interaction.followup.send(
            f"**{name}**\n"
            f"Rating: `{rating}`\n"
            f"Tags: `{', '.join(tags) if tags else 'No tags'}`\n"
            f"{problem_url}"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(BasicCommands(bot)) #add cog BasicCommands to bot

