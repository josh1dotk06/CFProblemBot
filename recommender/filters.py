
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


def filter_by_exclude_tags(problems: list[dict], exclude_tags: list[str]) -> list[dict]:

    filtered = []

    for problem in problems:
        problem_tags = problem.get("tags", [])
        is_allowed = True

        for tag in exclude_tags:
            if tag not in problem_tags:
                continue
            else:
                is_allowed = False
                break

        if is_allowed:
            filtered.append(problem)

    return filtered


            


            

