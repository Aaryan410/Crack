import database
import random
from session.interview import InterviewSession
from ai.evaluator import evaluate, evaluate_report 
from prompt.builder import build_report_prompt


# Printing UI

print('=' * 40)
print("Crack")
print("AI Interview Coach")
print('=' * 40)

# Asking for roles, no. of questions and difficulty
user_role = input("Role: ")
selected_difficulty = input("Difficulty: ")
number_of_questions = int(input("Number of Questions: "))

# Role and topics
role_folder = user_role.replace(" ", "_").lower()

# Accessing the Data
questions = database.load_questions(role_folder)

# Filtering questions by difficulty 
filtered_questions = []

for question in questions:
    if question["difficulty"] == selected_difficulty:
        filtered_questions.append(question)

# Error handling
if number_of_questions > len(filtered_questions):
    print("Not enough questions available")
    exit()

# How many Questions?
selected_questions = random.sample(filtered_questions, number_of_questions)

# Printing questions
session = InterviewSession(
    user_role,
    selected_difficulty,
    selected_questions
)

session.start()

while True:

    question = session.next_question()
    
    if question is None:
        break

    print('=' * 40)
    print(f"Question {session.current_index + 1}/{number_of_questions}")
    print('=' * 40)

    print(question["question"])

    answer = input("Answer: ")

    session.submit_answer(answer)

    evaluation = evaluate(session)

session.finish()

report = evaluate_report(session)

print('=' * 40)
print("INTERVIEW REPORT")
print('=' * 40)
print()
print(f"Overall Score: {report['overall_score']}")
print()
print(f"Technical Accuracy : {report['technical_accuracy']}")
print(f"communication      : {report['communication']}")
print(f"Confidence         : {report['confidence']}")

print('-' * 40)
print("Summary")
print('-' * 40)
print()
print(f"{report['summary']}")
print()

print('-' * 40)
print("Strengths")
print('-' * 40)
print()

for strength in report['strengths']:
    print(f"✓ {strength}")

print()

print('-' * 40 )
print("Weaknesses")
print('-' * 40)
print()

for weakness in report['weaknesses']:
    print(f"• {weakness}")

print()
print('-' * 40)
print("Recommendations")
print('-' * 40)
print()

for recommendation in report['recommendations']:
    print(f"→ {recommendation}")

print()


time_taken = session.ended_at - session.started_at
    
print(round(time_taken.total_seconds(), 2))
print("Interview Complete!")
print(f"Questions Answered: {number_of_questions}")
