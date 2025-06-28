import glob
import sys
import os
from enum import Enum
import random
from constants import topics
from collections import defaultdict
from timeit import default_timer as timer
import datetime
import argparse
import itertools
import json
import re

ProblemType = Enum('ProblemType', 'Top Freq Easiest Hardest Common Random')

def load_completed_list(user_data):
    completed1 = set()
    with open('completed.csv', 'r') as f:
        for line in f.read().splitlines():
            try:
                completed1.add(int(line.split(',')[0].strip()))
            except ValueError:
                continue
    completed2 = set(user_data["completed"])
    # TODO handle skipped, revisit, refresh lists
    return completed1.union(completed2)

def load_json(filename):
    with open(filename) as json_file:
        return json.load(json_file)

def load_user_data():
    return load_json('user.json')

def pick_problems(user_data, problems, topic_list, exclude_topics=None, difficulty_list=None, k=5, problem_type=ProblemType.Random):
    # Get problems matching the requested topics
    selected_topics = set(itertools.chain(*[topics.get(topic,[]) for topic in topic_list]))
    
    # Get problems to exclude based on excluded topics
    excluded_problems = set()
    if exclude_topics:
        excluded_problems = set(itertools.chain(*[topics.get(topic,[]) for topic in exclude_topics]))

    skip_set = set(load_completed_list(user_data))
    for maybe_skip in ['hard', 'revisit', 'refresh']:
        skip_set.update(user_data[maybe_skip] if maybe_skip not in args.list else [])

    problems_set = set(problems)
    all_problems_set = set(int(key) for key in all_problems.keys())
    
    # Apply inclusion and exclusion filters
    problem_set = (problems_set & selected_topics & all_problems_set) - skip_set - excluded_problems
    
    # Filter by difficulty if specified
    if difficulty_list:
        difficulty_problems = set()
        for problem_id in problem_set:
            problem_info = all_problems.get(str(problem_id))
            if problem_info and problem_info.get('Difficulty') in difficulty_list:
                difficulty_problems.add(problem_id)
        problem_set = difficulty_problems
        
    if problem_type==ProblemType.Random:
        return random.sample(list(problem_set), min(len(problem_set),k))
    return []

def mark_completed(leetcode_id, was_solved, num_errs, time):
    # problem# / was completed / time spent / num mistakes (if completed)
    # todo: internally track: last attempted date, too long, easy/medium/hard, acceptance rate, thumbs up/down, number attempts
    with open('completed.csv', 'a') as f:
        f.write(f'\n{leetcode_id},{was_solved},{num_errs},{time},{datetime.datetime.now():%Y-%m-%d}')

def mark_problem(user_data, mark_type, leetcode_id):
    user_data[mark_type].append(leetcode_id)
    with open('user.json', 'w') as f:
        f.write(re.sub(r',\n    ', ',', json.dumps(user_data, indent=2)))

def print_info(all_problems, problem_to_companies, my_companies, leetcode_id):
    problem = all_problems[str(leetcode_id)]
    difficulty_string = "medium difficulty" if problem['Difficulty'] == "Medium" else "considered easy" if problem['Difficulty'] == 'Easy' else problem['Difficulty']
    print(f"{leetcode_id} {problem['Name']} is {difficulty_string}: {problem['Acceptance']} of submissions pass")
    company_list = my_companies & set(problem_to_companies[str(leetcode_id)])
    company_list_string = f"including: {', '.join(company_list)}" if len(company_list) > 0 else f"including: {','.join(problem_to_companies[str(leetcode_id)][:5])}"
    print(f"{len(company_list)} companies have asked this question {company_list_string}")

def show_helper_menu():
    """Interactive helper menu to guide users in building their command"""
    print("\n===== LeetCode Problem Picker Helper Menu =====\n")
    print("This wizard will help you build a command to run. Let's go step by step.\n")
    
    # 1. Select topics
    print("AVAILABLE TOPICS:")
    
    # Create a set of canonical topics (remove aliases)
    # We'll consider a topic an alias if its problem list is identical to another topic
    canonical_topics = {}
    problem_sets = {}
    
    # First, create a mapping of problem sets to topic names
    for topic, problems in topics.items():
        problem_set_key = tuple(sorted(problems))  # Convert list to sorted tuple for hashing
        if problem_set_key in problem_sets:
            # This is an alias, skip it
            continue
        else:
            problem_sets[problem_set_key] = topic
            canonical_topics[topic] = problems
    
    # Now display the canonical topics in two columns
    topic_keys = sorted(list(canonical_topics.keys()))
    col_width = 30
    for i in range(0, len(topic_keys), 2):
        if i + 1 < len(topic_keys):
            # Two columns if we have enough topics
            print(f"{i+1:2d}. {topic_keys[i]:<{col_width}} {i+2:2d}. {topic_keys[i+1]}")
        else:
            # Just one column for the last odd item
            print(f"{i+1:2d}. {topic_keys[i]}")
    
    topic_indices = input("\nEnter topic numbers to include (comma-separated, or 'all'), leave blank for all topics: ")
    selected_topics = []
    if topic_indices.strip() and topic_indices.lower() != 'all':
        try:
            indices = [int(idx.strip()) for idx in topic_indices.split(',')]
            selected_topics = [topic_keys[idx-1] for idx in indices if 0 < idx <= len(topic_keys)]
        except ValueError:
            print("Invalid input. Using all topics.")
    
    # 2. Select topics to exclude
    exclude_indices = input("\nEnter topic numbers to EXCLUDE (comma-separated), leave blank to exclude none: ")
    excluded_topics = []
    if exclude_indices.strip():
        try:
            indices = [int(idx.strip()) for idx in exclude_indices.split(',')]
            excluded_topics = [topic_keys[idx-1] for idx in indices if 0 < idx <= len(topic_keys)]
        except ValueError:
            print("Invalid input. Excluding no topics.")
            
    # Map selected topics back to all valid topic names (including aliases)
    # This ensures the command works with the original topic names
    all_selected_topics = selected_topics.copy()
    all_excluded_topics = excluded_topics.copy()
    
    # 3. Select difficulty
    print("\nDIFFICULTY OPTIONS:")
    print("1. Easy\n2. Medium\n3. Hard")
    diff_input = input("Enter difficulty numbers (comma-separated), leave blank for all: ")
    selected_difficulty = []
    if diff_input.strip():
        diff_map = {1: 'Easy', 2: 'Medium', 3: 'Hard'}
        try:
            indices = [int(idx.strip()) for idx in diff_input.split(',')]
            selected_difficulty = [diff_map[idx] for idx in indices if idx in diff_map]
        except ValueError:
            print("Invalid input. Using all difficulties.")
    
    # 4. Problem list
    print("\nPROBLEM LIST OPTIONS:")
    print("1. blind75 (default)\n2. all (all available problems)\n3. Other (specify)")
    list_input = input("Choose a problem list option (1-3): ")
    problem_list = ['blind75']
    if list_input.strip() == '2':
        problem_list = ['all']
    elif list_input.strip() == '3':
        custom_list = input("Enter custom list name: ")
        if custom_list.strip():
            problem_list = [custom_list]
    
    # 5. Number of problems
    num_problems = 5
    try:
        num_input = input("\nHow many problems do you want? (default: 5): ")
        if num_input.strip():
            num_problems = int(num_input)
    except ValueError:
        print("Invalid input. Using default (5).")
    
    # 6. Interactive mode
    interactive = input("\nDo you want to use interactive mode? (y/n, default: n): ").lower().startswith('y')
    
    # Build command
    cmd = ["python", "lcpp.py"]
    if selected_topics:
        topic_args = ['-t'] + [f'"{t}"' if ' ' in t else t for t in selected_topics]
        cmd.extend(topic_args)
    if excluded_topics:
        exclude_args = ['-e'] + [f'"{t}"' if ' ' in t else t for t in excluded_topics]
        cmd.extend(exclude_args)
    if selected_difficulty:
        diff_args = ['-d'] + selected_difficulty
        cmd.extend(diff_args)
    if problem_list:
        list_args = ['-l'] + problem_list
        cmd.extend(list_args)
    cmd.extend(['-k', str(num_problems)])
    if interactive:
        cmd.append('-i')
    
    # Display and execute
    cmd_str = ' '.join(cmd)
    print("\n===== COMMAND GENERATED =====")
    print(cmd_str)
    print("==============================")
    
    execute = input("\nExecute this command now? (y/n): ").lower().startswith('y')
    if execute:
        print("\nExecuting command...\n")
        os.system(cmd_str)
    else:
        print("Command not executed. You can copy and paste it manually.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="",

    )
    parser.add_argument('--interactive', '-i', action='store_true', default=False, help='Easily log results while doing leetcode problems')
    parser.add_argument('--topic_list', '-t', nargs='+', default=topics.keys(),
                        help='List of subjects to filter on. '
                             'Options are: '
                             'array hash table ll greedy backtrack graph etc')
    parser.add_argument('--exclude_topics', '-e', nargs='+', default=None,
                        help='List of subjects to exclude from results')
    parser.add_argument('--list', '-l', nargs='+', default=['blind75'], help="Companies interested in (or file(s) containing comma-delimited problems)")
    parser.add_argument('--difficulty', '-d', nargs='+', choices=['Easy', 'Medium', 'Hard'], 
                        help="Filter problems by difficulty level(s)")
    parser.add_argument('--num_problems', '-k', type=int, default=5, help="Determine number of problems to solve")
    parser.add_argument('--info', action='store', type=int, help="Get details on a problem ID")
    parser.add_argument('--help-menu', '-m', action='store_true', default=False, help="Show interactive helper menu to build command")

    args = parser.parse_args()

    user_data = load_user_data()

    easy_set, medium_set, hard_set = set(), set(), set()
    # also store in sorted list for binsearch range lookup: https://stackoverflow.com/a/2899190

    problem_to_companies = load_json('problem_to_companies.json')
    company_to_problems = load_json('company_to_problems.json')
    all_problems = load_json('all_problems.json')
    my_companies = set(user_data["faang"] + user_data["my_companies"])

    #populate company file w/ maximum of 4 lines (sorted). each line is a comma separated list of problem numbers.
        # question: does 1yr,2yr and alltime contain 6mo? does 2yr contain 1yr? I think not?
        # 6mo
        # 1yr
        # 2yr
        # alltime
    problem_set = set()
    if 'all' in [e.lower() for e in args.list]:
        # If 'all' is specified, include all problem IDs from all_problems
        problem_set = set(int(key) for key in all_problems.keys())
    else:
        for elem in args.list:
            if elem in company_to_problems:
                for duration in company_to_problems[elem]:
                    problem_set.update([int(leetcode_id) for leetcode_id in company_to_problems[elem][duration]])
            elif elem.lower() in user_data:
                # load from file
                problem_set.update(user_data[elem.lower()])

    if args.help_menu:
        show_helper_menu()
        sys.exit(0)
        
    print_info_func = lambda id: print_info(all_problems, problem_to_companies, my_companies, id)
    if args.info:
        print_info_func(args.info)
    elif args.interactive:
        problems = pick_problems(user_data, problems=problem_set, topic_list=args.topic_list, exclude_topics=args.exclude_topics, difficulty_list=args.difficulty, k=args.num_problems)
        problem_set -= set(problems)

        if len(problems) == 0:
            print("You have completed all the problems in the selected set. Re-picking from the entire problem set")
            problems = pick_problems(user_data, problems=set(range(1,1700)), topic_list=args.topic_list, exclude_topics=args.exclude_topics, difficulty_list=args.difficulty, k=args.num_problems)
        if len(problems) == 0:
            print("Your --topic_list is either invalid or all completed. Repicking from all topics.")
            problems = pick_problems(user_data, problems=problem_set, topic_list=topics.keys(), exclude_topics=args.exclude_topics, difficulty_list=args.difficulty, k=args.num_problems)
        if len(problems) == 0:
            problems = pick_problems(user_data, problems=set(range(1,1700)), topic_list=topics.keys(), exclude_topics=args.exclude_topics, difficulty_list=args.difficulty, k=args.num_problems)

        valid_inputs = ["info", "hint", "easy", "hard", "quit", "pause", "break"]
        print(f"Other valid inputs: {', '.join(valid_inputs)}")
        
        for (idx,leetcode_id) in enumerate(problems):
            problem = all_problems[str(leetcode_id)]
            msg = "First problem" if idx == 0 else "Last problem" if idx == args.num_problems-1 else "Next up"
            print(f"\n{msg}:\n{leetcode_id}: {problem['Name']} {problem['Link']}")
            start_time = timer()
            while True:
                inp = input('When completed, enter: y/n,[num_errs],[time]\n')
                if inp.startswith('q'):
                    quit()
                if inp == 'hint':
                    # TODO need problem to topic dictionary
                    raise Exception("Not Implemented Yet")
                elif inp == 'info':
                    print_info_func(leetcode_id)
                    difficulty_string = "medium difficulty" if problem['Difficulty'] == "Medium" else "considered easy" if problem['Difficulty'] == 'Easy' else problem['Difficulty']
                    print(f"{leetcode_id} {problem['Name']} is {difficulty_string}: {problem['Acceptance']} of submissions pass")
                    company_list = my_companies & set(problem_to_companies[str(leetcode_id)])
                    company_list_string = f"including: {', '.join(company_list)}" if len(company_list) > 0 else f"including: {','.join(problem_to_companies[str(leetcode_id)][:5])}"
                    print(f"{len(company_list)} companies have asked this question {company_list_string}")
                elif inp == 'pause':
                    pause_time = timer()
                    input("Paused. Press Enter to continue the clock\n")
                    start_time = pause_time - start_time + timer()
                elif inp == 'break':
                    input("Paused. Press Enter to reset the clock and start the problem\n")
                    start_time = timer()
                elif inp == 'easy':
                    mark_completed(leetcode_id, 'yes', '0', '5')
                    # Replace with new problem not in problems
                    leetcode_id = pick_problems(user_data, problems=problem_set, topic_list=args.topic_list, difficulty_list=args.difficulty, k=1)[0]
                    problem_set.discard(leetcode_id)
                    problem = all_problems[str(leetcode_id)]
                    print(f"\n{msg}:\n{leetcode_id}: {problem['Name']} {problem['Link']}")
                    start_time = timer()
                elif inp == 'hard':
                    mark_problem(user_data, 'hard', leetcode_id)
                    leetcode_id = pick_problems(user_data, problems=problem_set, topic_list=args.topic_list, k=1)[0]
                    problem_set.discard(leetcode_id)
                    problem = all_problems[str(leetcode_id)]
                    print(f"\n{msg}:\n{leetcode_id}: {problem['Name']} {problem['Link']}")
                    # TODO pick problem with same topic and higher acceptance rate (if possible). If none, default to above line
                    start_time = timer()
                elif inp == 'skip':
                    try:
                        leetcode_id = pick_problems(user_data, problems=problem_set, topic_list=args.topic_list, exclude_topics=args.exclude_topics, difficulty_list=args.difficulty, k=1)[0]
                        start_time = timer()
                    except IndexError:
                        break
                elif inp.startswith('revisit'):
                    marked_id = int(inp.split(' ')[1]) if len(inp.split(' ')) > 0 else leetcode_id
                    mark_problem(user_data, 'revisit', marked_id)
                elif inp.startswith('refresh'):
                    marked_id = int(inp.split(' ')[1]) if len(inp.split(' ')) > 0 else leetcode_id
                    mark_problem(user_data, 'refresh', marked_id)
                elif inp.startswith('y') or inp.startswith('n'):
                    # log entry into csv
                    entry = inp.split(',')
                    was_solved = 'yes' if entry[0].startswith('y') else 'no'
                    num_errs = entry[1] if len(entry) > 1 else '0'
                    true_time = round((timer()-start_time)/60)
                    time = entry[2] if len(entry) > 2 else true_time

                    mark_completed(leetcode_id, was_solved, num_errs, time)
                    print(f"completed in {true_time}min")
                    break
                elif inp == 'help':
                    #print_help_screen()
                    print("TODO. For now, read the code or just try it out")
                    None
                else:
                    print(f"Invalid input. Type help for more options")
    else:
        print(pick_problems(user_data, problems=problem_set, topic_list=args.topic_list, exclude_topics=args.exclude_topics, difficulty_list=args.difficulty, k=args.num_problems))