import discord
from discord.ext import commands
from config import DISCORD_BOT_TOKEN, TEST_GUILD_ID

print("main.py started")

class ProblemSelectorBot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension("bot.commands")

        if TEST_GUILD_ID is not None:
            guild = discord.Object(id=TEST_GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            synced_commands = await self.tree.sync(guild=guild)

            print(f"Synced {len(synced_commands)} command(s) to test guild {TEST_GUILD_ID}.")
        else:
            synced_commands = await self.tree.sync()
            print(f"Synced {len(synced_commands)} global command(s).")


intents = discord.Intents.default()

bot = ProblemSelectorBot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}.")
    print("Bot is ready.")

if __name__ == "__main__":
    print("about to run bot")
    bot.run(DISCORD_BOT_TOKEN)