### HELPERS
def get_problem_id(problem: dict) -> str | None:
    contestId = problem.get("contestId")
    index = problem.get("index")

    if contestId is None or index is None:
        return None

    #unique problem identifier
    return f"{contestId}{index}"


def build_solved_problems(submissions: list[dict]) -> set[str]:
    solved_problems = set()

    for submission in submissions:
        if submission.get("verdict") != "OK": #solved
            continue

        problem = submission.get("problem", {})
        pId = get_problem_id(problem)
        if pId is not None:
            solved_problems.add(pId)

    return solved_problems


def build_contest_start_time(contests: list[dict]) -> dict[int, int]:
    """{
    1703: 1659200000,
    1800: 1670000000
}
    """

    contest_start_times = {}
    for contest in contests:
        contest_id = contest.get("id")
        contest_start = contest.get("startTimeSeconds")

        if contest_id is None or contest_start is None:
            continue

        contest_start_times[contest_id] = contest_start

    return contest_start_times



###ACTUAL FILTERS

def filter_by_rating(problems: list[dict], min_rating: int | None, max_rating: int | None) -> list[dict]:
    #lets keep only the problems within the range
     filtered = []

    #basic checking
     for problem in problems:
        rating = problem.get("rating")

        if min_rating is not None or max_rating is not None:
            if rating is None:
                continue        

        if min_rating is not None and rating < min_rating:
            continue

        if max_rating is not None and rating > max_rating:
            continue

        filtered.append(problem)

     return filtered

def parse_tags(tags_text: str | None) -> list[str]:
    #Convert a comma separated tag string into a clean list of tags eg: "greedy, binary search" to ["greedy", "binary search"]
    #we need to convert discord input into a list. We need this so we can compare desired input with the list format for tags in the JSON
    if tags_text is None:
        return []

    tags = []

    for tag in tags_text.split(","):
        cleaned_tag = tag.strip().lower()

        if cleaned_tag:
            tags.append(cleaned_tag)

    return tags

#keep only problems that contain included tags
def filter_by_include_tags(problems: list[dict], include_tags: list[str]) -> list[dict]:

    filtered = []

    for problem in problems:

        is_included = True
        problem_tags = problem.get("tags", [])

        #ensure that the tags in included tags are IN the tags of the problem. For exact tags, just switch them
        for tag in include_tags:
            if tag in problem_tags:
                continue
            else:
                is_included = False
                break
        
        if is_included:
            filtered.append(problem)

    return filtered

def filter_by_exact_tags(problems: list[dict], exact_tags: list[str]) -> list[dict]:
    #use sets instead of list, convert list into set thus
    if not exact_tags:
        return problems

    filtered = []
    exact_tag_set = set(exact_tags)

    #the idea is to just set-ialize the lists and just compare them so they are both exactly the same. List comparison wouldnt work since they are order sensitive
    for problem in problems:
        problem_tags = problem.get("tags", [])
        problem_tag_set = set(problem_tags)

        if problem_tag_set == exact_tag_set:
            filtered.append(problem)

    return filtered

def filter_by_exclude_tags(problems: list[dict], exclude_tags: list[str]) -> list[dict]:

    filtered = []

    for problem in problems:
        problem_tags = problem.get("tags", [])
        is_allowed = True

        #for each of the problem, we ensure that the tags in excluded tags is NOT in the problem tags
        for tag in exclude_tags:
            if tag not in problem_tags:
                continue
            else:
                is_allowed = False
                break

        if is_allowed:
            filtered.append(problem)

    return filtered


def filter_by_unseen(problems: list[dict], solved_problems: set[str]) -> list[dict]:
    filtered = []

    for problem in problems:
        problem_id = get_problem_id(problem)

        if problem_id is None:
            continue

        if problem_id in solved_problems:
            continue

        filtered.append(problem)
            
    return filtered


def filter_by_date(problems: list[dict], time: int | None, direction: str | None, contest_start_times: dict[int, int]) -> list[dict]:

    if time is None or direction is None:
        return problems

    filtered = []

    for problem in problems:
        contest_id = problem.get("contestId")
        if contest_id is None:
            continue

        pTime = contest_start_times[contest_id]
        if pTime is None:
            continue
    
        if direction == "after":
            if pTime >= time:
                filtered.append(problem)
        elif direction == "before":
            if pTime <= time:
                filtered.append(problem)

    return filtered


