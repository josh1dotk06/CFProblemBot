import os
from dotenv import load_dotenv 

load_dotenv() 


DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
TEST_GUILD_ID_RAW = os.getenv("TEST_GUILD_ID")

TEST_GUILD_ID = int(TEST_GUILD_ID_RAW) if TEST_GUILD_ID_RAW else None


if not DISCORD_BOT_TOKEN:
    raise RuntimeError("missing discord bot token in env file")



