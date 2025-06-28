#!/usr/bin/env python3
import os
import shutil

def move_file(filename, destination='data'):
    """Move a file to the data directory if it exists."""
    if os.path.exists(filename):
        if not os.path.exists(destination):
            os.makedirs(destination)
        dest_path = os.path.join(destination, filename)
        shutil.copy2(filename, dest_path)
        print(f"Moved {filename} to {dest_path}")
    else:
        print(f"File {filename} not found")

# Data files to move
files_to_move = [
    'all_problems.json',
    'company_to_problems.json',
    'problem_to_companies.json',
    'user.json',
    'completed.csv'
]

# Move each file
for file in files_to_move:
    move_file(file)

print("All data files moved to the data directory.")
print("After confirming everything works, you can delete the original files.")
