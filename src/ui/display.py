def print_info(all_problems, problem_to_companies, my_companies, leetcode_id):
    problem = all_problems[str(leetcode_id)]
    difficulty_string = "medium difficulty" if problem['Difficulty'] == "Medium" else "considered easy" if problem['Difficulty'] == 'Easy' else problem['Difficulty']
    print(f"{leetcode_id} {problem['Name']} is {difficulty_string}: {problem['Acceptance']} of submissions pass")
    company_list = my_companies & set(problem_to_companies[str(leetcode_id)])
    company_list_string = f"including: {', '.join(company_list)}" if len(company_list) > 0 else f"including: {','.join(problem_to_companies[str(leetcode_id)][:5])}"
    print(f"{len(company_list)} companies have asked this question {company_list_string}")

def show_helper_menu(topics):
    """Interactive helper menu to guide users in building their command"""
    print("\n===== LeetCode Problem Picker Helper Menu =====\n")
    print("This wizard will help you build a command to run. Let's go step by step.\n")
    
    # 1. Select topics
    print("AVAILABLE TOPICS:")
    
    # Create a set of canonical topics (remove aliases)
    canonical_topics = {}
    problem_sets = {}
    
    # First, create a mapping of problem sets to topic names
    for topic, problems in topics.items():
        problem_set_key = tuple(sorted(problems))
        if problem_set_key in problem_sets:
            continue
        else:
            problem_sets[problem_set_key] = topic
            canonical_topics[topic] = problems
    
    # Now display the canonical topics in two columns
    topic_keys = sorted(list(canonical_topics.keys()))
    col_width = 30
    for i in range(0, len(topic_keys), 2):
        if i + 1 < len(topic_keys):
            print(f"{i+1:2d}. {topic_keys[i]:<{col_width}} {i+2:2d}. {topic_keys[i+1]}")
        else:
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
    import os
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
        
    return {
        'topics': selected_topics,
        'excluded_topics': excluded_topics,
        'difficulty': selected_difficulty,
        'problem_list': problem_list,
        'num_problems': num_problems,
        'interactive': interactive
    }
