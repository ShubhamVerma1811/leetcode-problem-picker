import datetime
import json
import re
import os


def get_data_path(filename):
    if filename.startswith("data/"):
        return filename
    return os.path.join("data", filename)


def mark_completed(leetcode_id, was_solved, num_errs, time):
    with open(get_data_path("completed.csv"), "a") as f:
        f.write(
            f"\n{leetcode_id},{was_solved},{num_errs},{time},{datetime.datetime.now():%Y-%m-%d}"
        )


def mark_problem(user_data, mark_type, leetcode_id):
    user_data[mark_type].append(leetcode_id)
    with open(get_data_path("user.json"), "w") as f:
        f.write(re.sub(r",\n    ", ",", json.dumps(user_data, indent=2)))
