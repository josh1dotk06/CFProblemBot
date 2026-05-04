#responsible for saving and loading connected users, probably knows about user.json
import json
from pathlib import Path

USERS_FILE = Path("data/users.json")

def load_users() -> dict:
    #load all connected users from the json and give a dict mapping of discord user ids to cf handles 

    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not USERS_FILE.exists():
        #initialize the file
        USERS_FILE.write_text("{}", encoding="utf-8")
        return {}

    with USERS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)



def save_users(users: dict) -> None:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)

    #write it this time
    with USERS_FILE.open("w", encoding="utf-8") as file:
        json.dump(users, file, indent=4)



#map discord id with cf handle and connect it (log it in the json)
def connect_user(discord_id: int, codeforces_handle: str) -> None:
    users = load_users()
    users[str(discord_id)] = codeforces_handle
    save_users(users)



def get_handle(discord_id: int) -> str | None:
    users = load_users()
    return users.get(str(discord_id))



