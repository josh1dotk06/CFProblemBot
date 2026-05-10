import asyncio
from scraper.problem_length_scraper import scrape_problem, ProblemScrapeError

#old poc
"""
async def main():
    #https://codeforces.com/problemset/problem/1703/B
    problem = {"contestId": 1703, "index": "B", "name": "ICPC Balloons"}

    try:
        result = await scrape_problem(problem)
    except ProblemScrapeError as error:
        print(f"Scraping failed: {error}")
        return

    print(f"Problem ID: {result['problem_id']}")
    print(f"URL: {result['url']}")
    print(f"Word count: {result['word_count']}")
    print(f"Length: {result['length']}")
    print()
    print("Preview:")
    print(result["preview"])

#how???
if __name__ == "__main__":
    asyncio.run(main())
"""

async def main():
    #https://codeforces.com/problemset/problem/1703/B
    problem = {"contestId": 1703, "index": "B", "name": "ICPC Balloons"}

    try:
        result = await scrape_problem(problem)
    except ProblemScrapeError as error:
        print(f"Scraping failed: {error}")
        return

    print(f"Problem ID: {result['problem_id']}")
    print(f"URL: {result['url']}")
    print(f"Word count: {result['word_count']}")
    print(f"Length: {result['length']}")

#how???
if __name__ == "__main__":
    asyncio.run(main())