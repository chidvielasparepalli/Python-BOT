import json
import os

PROGRESS_FILE = "progress.json"


def load_progress():

    if os.path.exists(PROGRESS_FILE):

        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:

            return json.load(f)

    return {"completed": [], "failed": [], "current_page": 1}


def save_progress(progress):

    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:

        json.dump(progress, f, indent=2)


def mark_completed(progress, question_name):

    if question_name not in progress["completed"]:

        progress["completed"].append(question_name)

    # Remove from failed if it was there
    if question_name in progress["failed"]:

        progress["failed"].remove(question_name)

    save_progress(progress)


def mark_failed(progress, question_name, error=""):

    if question_name not in progress["failed"]:

        progress["failed"].append(question_name)

    save_progress(progress)


def is_completed(progress, question_name):

    return question_name in progress["completed"]
