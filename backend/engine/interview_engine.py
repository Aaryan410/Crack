import database
from ai.evaluator import evaluate
import random

class InterviewEngine:
    def __init__(self, role):

        role_folder = role.replace(" ", "_").lower()

        questions = database.load_questions(role_folder)

        self.current_difficulty = "easy"

        self.easy_questions = []
        self.medium_questions = []
        self.hard_questions = []
        self.scenario_questions = []

        self.stage_scores = []

        self.questions_asked = 0

        self.current_average = 0
        

        for question in questions:
            if question["difficulty"] == "easy":
                self.easy_questions.append(question)
            elif question["difficulty"] == "medium":
                self.medium_questions.append(question)
            elif question["difficulty"] == "hard":
                self.hard_questions.append(question)
            elif question["difficulty"] == "scenario":
                self.scenario_questions.append(question)


    def get_next_question(self):
        
        pools = {
            "easy": self.easy_questions,
            "medium": self.medium_questions,
            "hard": self.hard_questions,
            "scenario": self.scenario_questions
        }

        pool = pools[self.current_difficulty]

        question = random.choice(pool)

        pool.remove(question)

        return question


    def update(self, evaluation):

        self.scores.append(evaluation["score"])

        self.current_average = sum(self.scores) / len(self.scores)

        self.update_difficulty()


    def update_difficulty(self):

        if self.current_average >= 95:
            self.current_difficulty = "scenario"
        elif self.current_average >= 85:
            self.current_difficulty = "hard"
        elif self.current_average >= 75:
            self.current_difficulty = "medium"
        else:
            self.current_difficulty = "easy"


    def should_end(self):
        ...

    def current_stats(self): 
        ...