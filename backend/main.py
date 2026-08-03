import database
import random
from session.interview import InterviewSession
from ai.evaluator import evaluate


# Printing UI

print('==========================================================================================')
print("Crack")
print("AI Interview Coach")
print('==========================================================================================')

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

session.finish()

evaluation = evaluate(session)

time_taken = session.ended_at - session.started_at
    
print(round(time_taken.total_seconds(), 2))
print("Interview Complete!")
print(f"Questions Answered: {number_of_questions}")
