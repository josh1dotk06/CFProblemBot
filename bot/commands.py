from typing import Optional, Literal
from datetime import datetime, timezone

import discord #import discord library in here
from discord import app_commands
from discord.ext import commands

#import our custom stuff from client and user_store
from codeforces.client import get_user_info, CodeforcesAPIError, get_problemset, get_user_submissions, get_contest
from storage.user_store import connect_user, get_handle

#generating random problem
import random 

from recommender.filters import (build_contest_start_time, filter_by_rating, filter_by_include_tags, filter_by_exclude_tags, parse_tags, filter_by_exact_tags, build_solved_problems, filter_by_unseen, filter_by_date, filter_by_length)

##HELPER

def time_conversion(datestr: str) -> int:
    #date will be something like 05/12/2019 i.e DD/MM/YYYY
    #since unix of 01/01/1970

    date = datetime.strptime(datestr, "%d/%m/%Y")
    date = date.replace(tzinfo=timezone.utc) #coordinates universal time, not local to account for timezone shifts
    unix_timestamp = int(date.timestamp())
    return unix_timestamp


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
    @app_commands.describe( #these are the options you can select
        unseen="Only recommend problems you have not solved yet.",
        min_rating="Minimum Codeforces problem rating.",
        max_rating="Maximum Codeforces problem rating.",
        include_tags="Comma separated tags to include, like greedy,binary search.",
        exclude_tags="Comma separated tags to exclude, like dp,math.",
        exact_match="Only allow problems with exactly the included tags.",
        count="Number of problems to generate.",
        date_limit="Filter by date 'DD/MM/YYYY, e.g., '01/01/2024' or '31/12/2023'.",
        length="Filter by cached problem length: short, medium, or long."
    )
    #initialize to default values
    async def generate(
        self,
        interaction: discord.Interaction,
        unseen: bool = False,
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None,
        include_tags: Optional[str] = None,
        exclude_tags: Optional[str] = None,
        exact_match: bool = False,
        count: app_commands.Range[int, 1, 10] = 1,
        time_direction: Optional[Literal["before", "after"]] = None,
        date_limit: Optional[str] = None,
        length: Optional[Literal["short", "medium", "long"]] = None
        
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

        #date filtering logic
        target_timestamp = None
        if time_direction or date_limit:
            if not time_direction or not date_limit:
                await interaction.followup.send("To filter by date, you must provide BOTH 'time_direction' and 'date_limit'.")
                return

            try:
                cleaned_date = date_limit.strip()
                target_timestamp = time_conversion(cleaned_date)
            except ValueError:
                await interaction.followup.send("Invalid date format. Please use exact DD/MM/YYYY (e.g., 05/12/2023).")
                return

        problemset = await get_problemset()
        #only consider the actual problems right now (not problemStatistics)
        problemset = problemset["problems"]

        #testing the 4 basic filters first
        include_tag_list = parse_tags(include_tags)
        exclude_tag_list = parse_tags(exclude_tags)

        ###UNSEEN FILTER APPLY
        if unseen:
            handle = get_handle(interaction.user.id)

            if handle is None:
                await interaction.followup.send("You need to connect your Codeforces handle first using '/connect' before using 'unseen=True'.")
                return

            try:
                submissions = await get_user_submissions(handle)
            except CodeforcesAPIError as error:
                await interaction.followup.send(f"could not fetch your codeforces submissions: {error}")
                return

            solved_problems = build_solved_problems(submissions)
            problemset = filter_by_unseen(problemset, solved_problems)

        ### APPLY RATING AND INCLUDED TAGS
        problemset = filter_by_rating(problemset, min_rating, max_rating)
        problemset = filter_by_include_tags(problemset, include_tag_list)

        ##FILTER EXACT TAGS OR EXCLUDED TAGS
        if exact_match == True:
            problemset = filter_by_exact_tags(problemset, include_tag_list)
        else:
            problemset = filter_by_exclude_tags(problemset, exclude_tag_list)

        ##FILTER BEFORE/AFTER DATE
        if target_timestamp is not None and time_direction is not None:
            try:
                contests = await get_contest()
            except CodeforcesAPIError as error:
                await interaction.followup.send(f"Could not fetch contests: `{error}`")
                return

            contest_start_times = build_contest_start_time(contests)
            problemset = filter_by_date(problemset, target_timestamp, time_direction, contest_start_times)
        
        ####FILTER PROBLEM LENGTH

        problemset = filter_by_length(problemset, length)

        #with lots of filters, it can get to the point where the number of valid problems are literally zero
        if len(problemset) == 0:
            await interaction.followup.send("No problems matched your filters. Try widening the rating range, removing tags, or changing the date filter.")
            return

        #with lots of filters, it can get to the point where the number of valid problems are so little that its less than the desired count number
        actual_count = min(count, len(problemset))
        selected_problems = random.sample(problemset, actual_count)

        response = []

        #neat little heads up message
        if actual_count < count:
            response.append(f"There does not exist {count} problems with the specified filters, so below are {actual_count} problems")

        for problem in selected_problems:
            name = problem.get("name")
            contest_id = problem.get("contestId")
            index = problem.get("index")
            rating = problem.get("rating")
            tags = problem.get("tags")
            problem_url = f"https://codeforces.com/problemset/problem/{contest_id}/{index}"


            response.append(
                f"**{name}**\n"
                f"Rating: `{rating}`\n"
                f"Tags: `{', '.join(tags) if tags else 'No tags'}`\n"
                f"{problem_url}"
            )

        await interaction.followup.send("\n\n".join(response))

async def setup(bot: commands.Bot):

    await bot.add_cog(BasicCommands(bot)) #add cog BasicCommands to bot

