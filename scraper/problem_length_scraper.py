import re
import aiohttp
import json
from bs4 import BeautifulSoup
from pathlib import Path




class ProblemScrapeError(Exception):
    pass

def get_problem_id(problem: dict) -> str | None:
    contestId = problem.get("contestId")
    index = problem.get("index")

    if contestId is None or index is None:
        return None

    #unique problem identifier
    return f"{contestId}{index}"

###PROBLEM LENGTH FILTERING IS ONLY SUPPORTED THROUGH LOCAL META DATA CACHE
###LIVE DATA SCRAPING IS RESTRICTED BY THE WEBSITE
###FORGET ABOUT THE BOTTOM 2 METHODS, ITS JUST PROOF OF CONCEPT I GUESS
def build_problem_url(problem: dict) -> str | None:
    contest_id = problem.get("contestId")
    index = problem.get("index")

    if contest_id is None or index is None:
        return None

    return f"https://codeforces.com/problemset/problem/{contest_id}/{index}"

async def fetch_problem_url(problem_url: str) -> str:

    ##our thing looks like a bot which is why we keep getting 403 error. lets just not do this, too risky
    headers = {"User-Agent": "CFProblemBot/1.0"}
    timeout = aiohttp.ClientTimeout(total=15)

    try:
        #http req to individual problem url
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            async with session.get(problem_url) as response:
                if response.status != 200:
                    raise ProblemScrapeError(f"Failed to fetch problem page. HTTP status: {response.status}")
                return await response.text()

    except aiohttp.ClientError as error:
        raise ProblemScrapeError("Could not connect to Codeforces problem page.") from error


###REAL STUFF
##scraping the data from the HTML code
def extract_statement_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    statement = soup.select_one("div.problem-statement")
    if statement is None:
        raise ProblemScrapeError("Could not find div.problem-statement on the page.")

    #remove the title, mem limit, and time limt at the top
    for header in statement.select(".header"):
        header.decompose()

    #also remove the sample input and output test blocks
    for tests in statement.select(".sample-tests"):
        tests.decompose()
    
    #no notes
    for note in statement.select(".note"):
        note.decompose()

    #random stuff for decoration
    for junk in statement.select("script, style"):
        junk.decompose()
    
    text = statement.get_text(" ", strip=True)
    #repeated whitespace into one space using regex
    text = re.sub(r"\s+", " ", text)

    return text

#helper
def count_words(text: str) -> int:
    words = re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text)
    return len(words)

def classify_length(word_count: int) -> str:
    if word_count <= 200:
        return "short"
    elif word_count > 200 and word_count <= 333:
        return "medium"
    elif word_count > 333:
        return "long"


#main (old poc)
"""
async def scrape_problem(problem: dict) -> dict:
    problem_id = get_problem_id(problem)
    url = build_problem_url(problem)

    if problem_id is None or url is None:
        raise ProblemScrapeError("Problem does not have a valid contestId/index.")
    
    #old
    
    html = await fetch_problem_url(url)
    statement = extract_statement_text(html)
    count = count_words(statement)
    length = classify_length(count)
    

    html = 
    return {"problem_id": problem_id, "word_count": word_count, "length": length, "url": problem_url, "preview": statement_text[:300]}
"""

LOCAL_HTML_DIR = Path("local_html")
def read_local_html(file_path: str | Path) -> str:
    path = Path(file_path)

    if not path.exists():
        raise ProblemScrapeError(f"Local HTML file not found: {path}")
    return path.read_text(encoding="utf-8", errors="ignore")


##pipe the plength data of a problem into p_length.json
PROBLEM_LENGTH_FILE = Path("data/p_length.json")
def load_problem_length() -> dict:
    PROBLEM_LENGTH_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not PROBLEM_LENGTH_FILE.exists():
        PROBLEM_LENGTH_FILE.write_text("{}", encoding="utf-8")
        return {}
    with PROBLEM_LENGTH_FILE.open("r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            #The file exists but is empty or contains invalid JSON.
            #Return an empty dict so save_problem_length can overwrite it later.
            return {}

def save_problem_length(scrape_result: dict) -> None:
    problem_lengths = load_problem_length()
    problem_id = scrape_result["problem_id"]
    problem_lengths[problem_id] = {
        "word_count": scrape_result["word_count"],
        "length": scrape_result["length"],
        "url": scrape_result["url"],
        "source": "manual_local_html"
    }

    with PROBLEM_LENGTH_FILE.open("w", encoding="utf-8") as file:
        json.dump(problem_lengths, file, indent=4)




async def scrape_problem(problem: dict, html_file_path: str | None = None) -> dict:
    problem_id = get_problem_id(problem)
    url = build_problem_url(problem)

    if problem_id is None or url is None:
        raise ProblemScrapeError("Problem does not have a valid contestId/index.")

    #optional
    if html_file_path is None:
        html_path = LOCAL_HTML_DIR / f"{problem_id}.html"
    else:
        html_path = Path(html_file_path)

    html = read_local_html(html_path)

    statement_text = extract_statement_text(html)
    word_count = count_words(statement_text)
    length = classify_length(word_count)

    return {
        "problem_id": problem_id,
        "word_count": word_count,
        "length": length,
        "url": url,
    }