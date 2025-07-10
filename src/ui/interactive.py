from timeit import default_timer as timer
from src.utils.problem_tracker import mark_completed, mark_problem
from src.utils.problem_picker import pick_problems
from src.ui.display import print_info


def interactive_mode(
    user_data,
    problem_set,
    args,
    all_problems,
    problem_to_companies,
    my_companies,
    topics,
):
    problems = pick_problems(
        user_data=user_data,
        all_problems=all_problems,
        problems=problem_set,
        topics=topics,
        topic_list=args.topic_list,
        exclude_topics=args.exclude_topics,
        difficulty_list=args.difficulty,
        k=args.num_problems,
    )
    problem_set -= set(problems)

    if len(problems) == 0:
        topic_str = ", ".join(args.topic_list)
        exclude_str = ", ".join(args.exclude_topics) if args.exclude_topics else "none"
        difficulty_str = ", ".join(args.difficulty) if args.difficulty else "any"
        print(f"No problems found matching all criteria:")
        print(f"Topics: {topic_str}")
        print(f"Excluded topics: {exclude_str}")
        print(f"Difficulty: {difficulty_str}")

        # Check for any uncompleted problems in the selected topic
        print("\nChecking for any uncompleted problems in your selected topics...")

        # Get all problems for selected topic
        all_topic_problems = set()
        for topic in args.topic_list:
            all_topic_problems.update(topics.get(topic, []))

        # Load the completed problems
        from src.data.loader import load_completed_list

        completed = set(load_completed_list(user_data))

        # Find non-completed problems for this topic
        remaining_topic_problems = all_topic_problems - completed

        if remaining_topic_problems:
            print(
                f"Found {len(remaining_topic_problems)} uncompleted problems in your selected topics."
            )
            print("What would you like to do?")
            print("1. Show uncompleted problems from my topic (ignore other filters)")
            print("2. Continue with original behavior (try problems from all topics)")

            choice = input("Enter choice (1-2): ")

            if choice == "1":
                # Show uncompleted problems from the selected topic(s)
                problems = pick_problems(
                    user_data=user_data,
                    all_problems=all_problems,
                    problems=remaining_topic_problems,
                    topics=topics,
                    topic_list=args.topic_list,
                    exclude_topics=None,  # Ignore exclusions
                    difficulty_list=None,  # Ignore difficulty
                    k=args.num_problems,
                )
            else:  # Default to choice 2 for any other input
                print("\nContinuing with original behavior...")
                # Continue with the original fallback logic
                # No need to do anything as the code below will execute
        else:
            print("\nAll problems for your selected topics have been completed!")

            # Try with all problems but keep other filters
            print("\nTrying to find problems from entire problem set...")
            problems = pick_problems(
                user_data=user_data,
                all_problems=all_problems,
                problems=set(range(1, 1700)),
                topics=topics,
                topic_list=args.topic_list,
                exclude_topics=args.exclude_topics,
                difficulty_list=args.difficulty,
                k=args.num_problems,
            )

            if len(problems) == 0:
                print(
                    "\nStill no matches. Will try ignoring topic filter and using all topics..."
                )
                problems = pick_problems(
                    user_data=user_data,
                    all_problems=all_problems,
                    problems=problem_set,
                    topics=topics,
                    topic_list=topics.keys(),
                    exclude_topics=args.exclude_topics,
                    difficulty_list=args.difficulty,
                    k=args.num_problems,
                )
    if len(problems) == 0:
        problems = pick_problems(
            user_data=user_data,
            all_problems=all_problems,
            problems=set(range(1, 1700)),
            topics=topics,
            topic_list=topics.keys(),
            exclude_topics=args.exclude_topics,
            difficulty_list=args.difficulty,
            k=args.num_problems,
        )

    valid_inputs = ["info", "hint", "easy", "hard", "quit", "pause", "break"]
    print(f"Other valid inputs: {', '.join(valid_inputs)}")

    for idx, leetcode_id in enumerate(problems):
        problem = all_problems[str(leetcode_id)]
        msg = (
            "First problem"
            if idx == 0
            else "Last problem" if idx == args.num_problems - 1 else "Next up"
        )
        print(f"\n{msg}:\n{leetcode_id}: {problem['Name']} {problem['Link']}")
        start_time = timer()
        while True:
            inp = input("When completed, enter: y/n,[num_errs],[time]\n")
            if inp.startswith("q"):
                return
            if inp == "hint":
                # TODO: implement hint feature
                print("Hint feature not implemented yet")
            elif inp == "info":
                print_info(
                    all_problems, problem_to_companies, my_companies, leetcode_id
                )
            elif inp == "pause":
                pause_time = timer()
                input("Paused. Press Enter to continue the clock\n")
                start_time = pause_time - start_time + timer()
            elif inp == "break":
                input("Paused. Press Enter to reset the clock and start the problem\n")
                start_time = timer()
            elif inp == "easy":
                mark_completed(leetcode_id, "yes", "0", "5")
                # Replace with new problem not in problems
                new_problems = pick_problems(
                    user_data=user_data,
                    all_problems=all_problems,
                    problems=problem_set,
                    topics=topics,
                    topic_list=args.topic_list,
                    difficulty_list=args.difficulty,
                    k=1,
                )
                if new_problems:
                    leetcode_id = new_problems[0]
                    problem_set.discard(leetcode_id)
                    problem = all_problems[str(leetcode_id)]
                    print(
                        f"\n{msg}:\n{leetcode_id}: {problem['Name']} {problem['Link']}"
                    )
                    start_time = timer()
            elif inp == "hard":
                mark_problem(user_data, "hard", leetcode_id)
                new_problems = pick_problems(
                    user_data=user_data,
                    all_problems=all_problems,
                    problems=problem_set,
                    topics=topics,
                    topic_list=args.topic_list,
                    k=1,
                )
                if new_problems:
                    leetcode_id = new_problems[0]
                    problem_set.discard(leetcode_id)
                    problem = all_problems[str(leetcode_id)]
                    print(
                        f"\n{msg}:\n{leetcode_id}: {problem['Name']} {problem['Link']}"
                    )
                    start_time = timer()
            elif inp == "skip":
                try:
                    leetcode_id = pick_problems(
                        user_data=user_data,
                        all_problems=all_problems,
                        problems=problem_set,
                        topics=topics,
                        topic_list=args.topic_list,
                        exclude_topics=args.exclude_topics,
                        difficulty_list=args.difficulty,
                        k=1,
                    )[0]
                    start_time = timer()
                except IndexError:
                    break
            elif inp.startswith("revisit"):
                parts = inp.split(" ")
                marked_id = int(parts[1]) if len(parts) > 1 else leetcode_id
                mark_problem(user_data, "revisit", marked_id)
            elif inp.startswith("refresh"):
                parts = inp.split(" ")
                marked_id = int(parts[1]) if len(parts) > 1 else leetcode_id
                mark_problem(user_data, "refresh", marked_id)
            elif inp.startswith("y") or inp.startswith("n"):
                entry = inp.split(",")
                was_solved = "yes" if entry[0].startswith("y") else "no"
                num_errs = entry[1] if len(entry) > 1 else "0"
                true_time = round((timer() - start_time) / 60)
                time = entry[2] if len(entry) > 2 else true_time

                mark_completed(leetcode_id, was_solved, num_errs, time)
                print(f"completed in {true_time}min")
                break
            elif inp == "help":
                print(
                    "Available commands: info, hint, easy, hard, quit, pause, break, skip, revisit, refresh"
                )
            else:
                print(f"Invalid input. Type help for more options")
