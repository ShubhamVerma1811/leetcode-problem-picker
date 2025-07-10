# leetcode-problem-picker

> **Note:** This project is vibe coded for my personal use. I don't use Python and have little knowledge of what's happening in the code. All changes are vibe coded using Windsurf AI.

LeetCode-Problem-Picker uses your history to select problems catered to your goals and needs.

Its purpose is to:
Track progress in order to identify and improve on areas of weakness
Choose problems that are most beneficial: frequently asked by the top tech companies
Ensure balance between all subjects with weighted rotation.

During my leetcode journey, I discovered the answer to "which problems should I do next?" depend on goals and progress:

1. **Topic Focus**: Narrow down to 1+ subjects e.g. "trees, graphs or DP". Intended for learning and focusing on weaknesses.
2. **Frequently Asked**: Questions from a list, e.g. ones asked by companies or list of Blind's Curated 75. The default.
3. **Level Up** (WIP): Deduces user's "skill range" for each topic in order to challenge appropriately.
4. **Weighted random** (TODO): Weighted towards questions with high like count, greater like/dislike ratio, etc.

## Setup:

`git clone https://github.com/shubhamverma1811/leetcode-problem-picker.git`

## Usage:

### Interactive Helper Menu (Recommended for beginners)

`python main.py -m`

This launches an interactive wizard that guides you through building your command. It will:

- Show all available topics in an organized layout
- Let you select topics by number instead of typing names
- Allow you to exclude specific topics
- Help you filter by difficulty level
- Generate and optionally execute the final command

### Command Line Options

`python main.py [-t stack trie graph dp] [-e graph dp] [--list airbnb google blind75 skipped] [-d Easy Medium Hard] [-k 5] [-i]`

```
--help-menu -m      launches interactive helper menu to build your command (recommended for beginners)
--topic_list -t     selects from a pool of problems associated with a subject (e.g. trie, greedy, graph)
--exclude_topics -e excludes problems that belong to specified topics (e.g. dp, graph)
--list -l           chooses problems from one or more text files (comma-delimited)
                    use 'all' to include all problems from all_problems.json
--difficulty -d     filters problems by difficulty level(s): Easy, Medium, Hard
--num_problems -k   number of problems to get
--interactive -i    interactive mode. Preferred way to input data. See section below for more info.
note: no topic or list will result in a problem randomly being selected
```

### Examples:

```bash
# Launch the interactive helper menu (easiest way for beginners)
python main.py -m

# Get 5 array problems
python main.py -t arr

# Get 10 linked list problems (using the alias)
python main.py -t ll -k 10

# Get 3 medium difficulty problems from the blind75 list
python main.py -d Medium -k 3

# Get hard topological sort problems from all problems
python main.py -t "top sort" -d Hard -l all

# Get both easy and medium problems from dynamic programming
python main.py -t dp -d Easy Medium -l all

# Get array problems but exclude those that are also graph problems
python main.py -t arr -e graph -l all

# Get linked list problems but exclude those that also involve recursion
python main.py -t ll -e recursion -l all
```

`python main.py --info 91`
![info usage](https://i.ibb.co/z7ndhVQ/Screen-Shot-2021-05-25-at-4-06-30-PM.png)
Displays information about a specific problem: Name, difficulty, Acceptance rate, and companies that ask it

## Interactive Mode:

This mode selects and displays a single problem and waits for input:

```
info                displays details about problem: problem name, difficulty, acceptance rate
hint                displays topics related to a solution
y/n,num_errs,time   Enter data regarding attempt. See next section for details
easy                mark as completed (quickly), then selects a different problem
hard                adds to a hard/skipped list. selects a less similar, less challenging problem
revisit [ID]        mark problem as one to revisit later
refresh [ID]        mark problem as one to "refresh" on later
pause               pause the timer
break               take a break. restarts the timer
quit                stop the program
```

### When No Problems Match All Criteria

If no problems match all your specified criteria (e.g., topics + difficulty + exclusions), the program will:

1. Display clear feedback about why no problems were found
2. Check if there are any uncompleted problems in your selected topics
3. If uncompleted problems exist, offer you a choice to:
   - Show uncompleted problems from your selected topics (ignoring other filters)
   - Continue with the original behavior (try problems from all topics)
4. If all problems in your selected topics are completed, it will notify you and try alternative selections

## Completed Problems (optional/recommended):

To maximize this program, you need to maintain a list of completed problems. This can be done in the following ways:

1. interactive mode: After completion of each assigned problem, the result is appended to completed.csv.
2. completed.txt: Best if you have a history of solving leetcode problems. The file expects a comma-delimited list of problem numbers e.g. `78,5,42,1337`
   To quickly populate with leetcode data:

- **Option 1 (Manual):** Login to leetcode and visit [your list of solved problems](https://leetcode.com/problemset/all/?status=Solved). Select "All" rows per page in the bottom-left dropdown.
  - Open up Developer Tools (F12) and run this line in your Console tab:
    `console.log(Array.from(document.querySelectorAll('.reactable-data tr td[label="#"]')).map(x => x.textContent).toString())`
  - Copy the list and save into completed.txt

- **Option 2 (Automated):** Use the provided script to automatically fetch your completed problems via LeetCode API:

  **Using a .env file (recommended):**
  1. Create a `.env` file in the project root (copy from `.env.example`)
  2. Add your LeetCode credentials to the file:
     ```
     LEETCODE_USERNAME=your_username
     LEETCODE_SESSION=your_session_cookie
     ```
  3. Run the script:
     ```bash
     python -m src.utils.fetch_completed
     ```

  **Using environment variables:**
  ```bash
  # Set environment variables with your LeetCode credentials
  export LEETCODE_USERNAME="your_username"
  export LEETCODE_SESSION="your_session_cookie"

  # Run the script to update completed.csv
  python -m src.utils.fetch_completed
  ```

  To get your LeetCode session cookie:
  1. Log in to LeetCode in your browser
  2. Open Developer Tools (F12) → Application tab → Cookies
  3. Find and copy the value of the `LEETCODE_SESSION` cookie

3. completed.csv: The file that interactive mode writes to. Provides details about attempt. One problem per line
   Expected format: `LC number,was solved,[num_errors],[time],[date]`

```
LC number           integer
was solved          string. valid inputs: y/n (or yes/no)
num_errors          number of mistakes made when solving problem
time                amount of time spent on the problem (minutes)
date                DateTime. date completed
```
