import json
from rich import print
from pyfiglet import Figlet
from pathlib import Path
import datetime
from session.interview import InterviewSession
from ai.evaluator import evaluate, evaluate_report 
from engine.interview_engine import InterviewEngine


# Printing UI
figlet_1 = Figlet(font = "slant", width = 150)
figlet_2 = Figlet(font = "slant", width = 100)

print('=' * 40)
print(figlet_1.renderText("Crack"))
print(figlet_2.renderText("AI Interview Coach"))
print('=' * 40)

# Asking for roles, no. of questions and difficulty
user_role = input("Role: ")

engine = InterviewEngine(user_role)

# Printing questions
session = InterviewSession(
    user_role,
    "adaptive"
)

session.start()

while not engine.should_end():

    question = engine.get_next_question()

    if question is None:
        break

    session.current_question = question

    session.question_started_at = datetime.datetime.now()

    print()
    print('=' * 40)
    print(f"Question {engine.questions_asked}")
    print('=' * 40)
    
    print(question['question'])

    answer = input("Answer: ")

    session.submit_answer(answer)

    evaluation = evaluate(session)

    if evaluation is None:
        print("[yellow]Couldn't get a score for that answer - its saved, moving on.[/yellow]")

    engine.update(evaluation)

session.finish()

print()
if engine.pool_exhausted:
    print("[yellow]Ran out of questions at this difficulty - wrapping with what we have.[/yellow]")
print("Evaluating answers........")
print()

report = evaluate_report(session)

print('=' * 40)
print(figlet_2.renderText("INTERVIEW REPORT"))
print('=' * 40)
print()
print(f"Overall Score: {report['overall_score']}")
print()
print(f"Technical Accuracy : {report['technical_accuracy']}")
print(f"communication      : {report['communication']}")
print(f"Confidence         : {report['confidence']}")

print('-' * 40)
print("[bold]Summary")
print('-' * 40)
print()
print(f"{report['summary']}")
print()

print('-' * 40)
print("[bold]Strengths")
print('-' * 40)
print()

for strength in report['strengths']:
    print(f"✓ {strength}")

print()

print('-' * 40 )
print("[bold]Weaknesses")
print('-' * 40)
print()

for weakness in report['weaknesses']:
    print(f"• {weakness}")

print()
print('-' * 40)
print("[bold]Recommendations")
print('-' * 40)
print()

for recommendation in report['recommendations']:
    print(f"→ {recommendation}")

print()


time_taken = session.ended_at - session.started_at
    
print(round(time_taken.total_seconds(), 2))
print("Interview Complete!")
print(f"Questions Answered: {engine.questions_asked}")

now = datetime.datetime.now()

history = {
    "role": user_role,
    "date": now.isoformat(),
    "overall_score": report['overall_score'],
    "summary": report['summary'],
    "questions_answered": engine.questions_asked,
    "final_stage": engine.current_difficulty,
    "time_taken": round(time_taken.total_seconds(), 2),
    "answers": [
        {
            "question": answer['question'],
            "answer": answer['answer'],
            "score": answer['score'],
            "feedback": answer['feedback'],
            "ideal_answer_summary": answer['ideal_answer_summary']
        }
        for answer in session.answers
    ]
}

BASE_DIR = Path(__file__).parent

folder_path = BASE_DIR / "history"
file_path = folder_path / f"{now.strftime("%Y-%m-%d_%H-%M.%S")}.json"

folder_path.mkdir(parents = True, exist_ok = True)

with open(file_path, "w", encoding = "utf-8") as f:
    json.dump(history, f, indent = 4, ensure_ascii = False)
