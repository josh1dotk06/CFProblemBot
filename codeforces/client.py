import aiohttp

#making codeforce api req so we can get that juicy data

CODEFORCES_API_BASE_URL = "https://codeforces.com/api"

#create our own custom error
class CodeforcesAPIError(Exception):
    pass

#get info for general codeforces api with optional parameters (only good for user info rn)
async def _get(method: str, params: dict | None = None) -> dict:

    url = f"{CODEFORCES_API_BASE_URL}/{method}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
    except aiohttp.ClientError as error:
        raise CodeforcesAPIError("Could not connect to Codeforces.") from error
    
    if data.get("status") != "OK":
        message = data.get("comment", "Unknown Codeforces API error.")
        raise CodeforcesAPIError(message)

    #all cf api json's use result as the key to the important data
    return data["result"]

#next iteration, get the problem set
async def get_problemset() -> dict:
    return await _get("problemset.problems")



async def get_user_info(handle: str) -> dict:
    result = _get("user.info", {"handles": handle})
    
    if len(result)==0:
        raise CodeforcesAPIError("No user was found with that handle on codeforces")

    #explaination for result[0], essentially the result key points to a list of dictionaries, but theres only 1 dictionary containing all the data, thus result[0] IS that dictionary
    return result[0]

