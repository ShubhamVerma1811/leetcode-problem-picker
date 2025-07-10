import json
import os


def get_data_path(filename):
    """Returns the absolute path to a data file"""
    if filename.startswith("data/"):
        return filename
    return os.path.join("data", filename)


def load_json(filename):
    with open(get_data_path(filename)) as json_file:
        return json.load(json_file)


def load_user_data():
    return load_json("user.json")


def load_all_data():
    user_data = load_user_data()
    problem_to_companies = load_json("problem_to_companies.json")
    company_to_problems = load_json("company_to_problems.json")
    all_problems = load_json("all_problems.json")
    my_companies = set(user_data["faang"] + user_data["my_companies"])

    return (
        user_data,
        problem_to_companies,
        company_to_problems,
        all_problems,
        my_companies,
    )


def load_completed_list(user_data):
    completed1 = set()
    csv_path = get_data_path("completed.csv")

    # Check if file exists, create if it doesn't
    if not os.path.exists(csv_path):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        # Create empty file
        with open(csv_path, "w") as f:
            pass

    # Read from existing file
    with open(csv_path, "r") as f:
        for line in f.read().splitlines():
            try:
                if line.strip():  # Skip empty lines
                    completed1.add(int(line.split(",")[0].strip()))
            except ValueError:
                continue

    # Add problems from user data if available
    completed2 = set(user_data.get("completed", []))
    return completed1.union(completed2)
