import random
import itertools
from src.data.loader import load_completed_list


def pick_problems(
    user_data,
    all_problems,
    problems,
    topics,
    topic_list,
    exclude_topics=None,
    difficulty_list=None,
    k=5,
    problem_type="Random",
):
    # Get problems matching the requested topics
    selected_topics = set(
        itertools.chain(*[topics.get(topic, []) for topic in topic_list])
    )

    # Get problems to exclude based on excluded topics
    excluded_problems = set()
    if exclude_topics:
        excluded_problems = set(
            itertools.chain(*[topics.get(topic, []) for topic in exclude_topics])
        )

    # Get skip set from completed problems and other lists
    skip_set = set(load_completed_list(user_data))
    for maybe_skip in ["hard", "revisit", "refresh"]:
        if maybe_skip in user_data:
            skip_set.update(user_data[maybe_skip])

    problems_set = set(problems)
    all_problems_set = set(int(key) for key in all_problems.keys())

    # Apply inclusion and exclusion filters
    problem_set = (
        (problems_set & selected_topics & all_problems_set)
        - skip_set
        - excluded_problems
    )

    # Filter by difficulty if specified
    if difficulty_list:
        difficulty_problems = set()
        for problem_id in problem_set:
            problem_info = all_problems.get(str(problem_id))
            if problem_info and problem_info.get("Difficulty") in difficulty_list:
                difficulty_problems.add(problem_id)
        problem_set = difficulty_problems

    if problem_type == "Random":
        return random.sample(list(problem_set), min(len(problem_set), k))

    return []
