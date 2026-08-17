from backend import database
import random

EASY_MIN_QUESTIONS = 2
MEDIUM_MIN_QUESTIONS = 2
HARD_MIN_QUESTIONS = 3

PROMOTION_SCORE = 90
PASS_SCORE = 80


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
        
        self.in_extension = False

        self.stage_questions = 0

        self.extra_questions = 0

        self.questions_asked = 0

        self.current_average = 0

        self.interview_failed = False

        self.interview_finished = False

        self.pool_exhausted = False

        self.last_evaluation_failed = False


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

        self.questions_asked += 1
        self.stage_questions += 1
        
        pools = {
            "easy": self.easy_questions,
            "medium": self.medium_questions,
            "hard": self.hard_questions,
            "scenario": self.scenario_questions
        }

        pool = pools[self.current_difficulty]

        if not pool:
            self.pool_exhausted = True
            self.interview_finished = True
            return None

        question = random.choice(pool)
        pool.remove(question)

        return question


    def update(self, evaluation):

        if evaluation is None or "score" not in evaluation:
            self.last_evaluation_failed = True
            return

        self.last_evaluation = False

        self.stage_scores.append(evaluation["score"])

        if self.in_extension:
            self.extra_questions -= 1

        self.current_average = (
            sum(self.stage_scores) / 
            len(self.stage_scores)
        )

        self.update_difficulty()


    def promote(self, difficulty):
        self.current_difficulty = difficulty

        self.stage_scores = []
        self.stage_questions = 0
        self.current_average = 0

        self.in_extension = False
        self.extra_questions = 0


    def update_difficulty(self):

        if self.current_difficulty == "easy":
            if self.stage_questions < EASY_MIN_QUESTIONS:
                return

            if self.in_extension:
                if self.extra_questions > 0:
                    return

                if self.current_average >= PASS_SCORE:
                    self.promote("medium")
                    return
                else:
                    self.interview_failed = True
                    return

            if self.current_average >= PROMOTION_SCORE:
                self.promote("medium")
                return
            elif self.current_average >= PASS_SCORE:
                self.in_extension = True
                self.extra_questions = random.randint(2, 3)
            else:
                self.in_extension = True
                self.extra_questions = 2
                return


        if self.current_difficulty == "medium":
            if self.stage_questions < MEDIUM_MIN_QUESTIONS:
                return

            if self.in_extension:
                if self.extra_questions > 0:
                    return

                if self.current_average >= PASS_SCORE:
                    self.promote("hard")
                    return
                else:
                    self.interview_failed = True
                    return

                return

            if self.current_average >= PROMOTION_SCORE:
                self.promote("hard")
                return
            elif self.current_average >= PASS_SCORE:
                self.in_extension = True
                self.extra_questions = random.randint(2, 3)
            else:
                self.in_extension = True
                self.extra_questions = 2
                return


        if self.current_difficulty == "hard":
            if self.stage_questions < HARD_MIN_QUESTIONS:
                return

            if self.in_extension:
                if self.extra_questions > 0:
                    return

                if self.current_average >= PASS_SCORE:
                    self.promote("scenario")
                    return
                else:
                    self.interview_failed = True
                    return

                return

            if self.current_average >= PROMOTION_SCORE:
                self.promote("scenario")
                return
            elif self.current_average >= PASS_SCORE:
                self.in_extension = True
                self.extra_questions = random.randint(2, 3)
            else:
                self.in_extension = True
                self.extra_questions = 2
                return


        if self.current_difficulty == "scenario":
            if not self.in_extension:
                self.in_extension = True
                self.extra_questions = random.randint(2, 3)

            if self.extra_questions > 0:
                return

            self.interview_finished = True


    def should_end(self):
        return self.interview_finished or self.interview_failed


    def current_stats(self): 
        return {
            "difficulty": self.current_difficulty,
            "average": self.current_average,
            "questions_asked": self.questions_asked,
            "stage_questions": self.stage_questions
        }