import aiohttp

#making codeforce api req so we can get that juicy data

CODEFORCES_API_BASE_URL = "https://codeforces.com/api"

#create our own custom error
class CodeforcesAPIError(Exception):
    pass

#get user info for the codeforces handle
async def get_user_info(handle: str) -> dict:
    url = f"{CODEFORCES_API_BASE_URL}/user.info"
    params = {"handles" : handle}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
    except aiohttp.ClientError as error:
        raise CodeforcesAPIError("Could not connect to Codeforces.") from error

    
    if data.get("status") != "OK":
        message = data.get("comment", "Unknown Codeforces API error.")
        raise CodeforcesAPIError(message)

    #result is the key for all of the user data, look at https://codeforces.com/api/user.info?handles=DmitriyH;Fefer_Ivan&checkHistoricHandles=false for further analysis
    users = data.get("result", [])

    #nothing stored in retrieved object -> no cf handle
    if len(users) == 0:
        raise CodeforcesAPIError("No Codeforces user was found with that handle.")

    return users[0]

#next iteration, get the problem set
async def get_problemset() -> dict:
