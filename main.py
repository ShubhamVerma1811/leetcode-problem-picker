#!/usr/bin/env python3
import sys
import argparse
import os
from src.data.loader import load_all_data
from src.ui.display import print_info, show_helper_menu
from src.utils.problem_picker import pick_problems
from src.ui.interactive import interactive_mode
from constants import topics

def main():
    parser = argparse.ArgumentParser(description="LeetCode Problem Picker")
    parser.add_argument('--interactive', '-i', action='store_true', default=False, help='Interactive mode')
    parser.add_argument('--topic_list', '-t', nargs='+', default=topics.keys(),
                      help='List of subjects to filter on')
    parser.add_argument('--exclude_topics', '-e', nargs='+', default=None,
                      help='List of subjects to exclude')
    parser.add_argument('--list', '-l', nargs='+', default=['blind75'], 
                      help="Companies interested in (or files containing comma-delimited problems)")
    parser.add_argument('--difficulty', '-d', nargs='+', choices=['Easy', 'Medium', 'Hard'], 
                      help="Filter problems by difficulty level(s)")
    parser.add_argument('--num_problems', '-k', type=int, default=5, help="Number of problems")
    parser.add_argument('--info', action='store', type=int, help="Get details on a problem ID")
    parser.add_argument('--help-menu', '-m', action='store_true', default=False, help="Show helper menu")
    
    args = parser.parse_args()
    
    # Load all data
    user_data, problem_to_companies, company_to_problems, all_problems, my_companies = load_all_data()
    
    # Build problem set based on arguments
    problem_set = set()
    
    if 'all' in [e.lower() for e in args.list]:
        problem_set = set(int(key) for key in all_problems.keys())
    else:
        for elem in args.list:
            if elem in company_to_problems:
                for duration in company_to_problems[elem]:
                    problem_set.update([int(leetcode_id) for leetcode_id in company_to_problems[elem][duration]])
            elif elem.lower() in user_data:
                problem_set.update(user_data[elem.lower()])
    
    # Handle command options
    if args.help_menu:
        show_helper_menu(topics)
        sys.exit(0)
    
    if args.info:
        print_info(all_problems, problem_to_companies, my_companies, args.info)
    elif args.interactive:
        interactive_mode(user_data, problem_set, args, all_problems, problem_to_companies, my_companies, topics)
    else:
        selected_problems = pick_problems(user_data, all_problems, problem_set, topics, args.topic_list, 
                                         args.exclude_topics, args.difficulty, args.num_problems)
        print(selected_problems)

if __name__ == "__main__":
    main()
