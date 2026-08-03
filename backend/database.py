import json 
from pathlib import Path


def load_questions(role):

    role_dir = Path(__file__).parent / "questions" / role

    json_files = list(role_dir.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {role_dir}")
    
    all_questions = []

    for json_file in json_files: 
        with open(json_file, "r", encoding = "utf-8") as file:
            data = json.load(file)
            all_questions.extend(next(iter(data.values())))

    return all_questions