import datetime


class InterviewSession:

    def __init__(self, role, difficulty = "adaptive"):
        self.role = role
        self.difficulty = difficulty

        self.current_question = None
        self.answers = []
        self.started_at = None
        self.ended_at = None
        self.question_started_at = None

    def start(self):
        if self.started_at is not None:
            return

        self.started_at = datetime.datetime.now()


    def submit_answer(self, answer):
        current_question = self.current_question

        current_time = datetime.datetime.now()

        if self.question_started_at is None:
            self.question_started_at = current_time

        time_taken = current_time - self.question_started_at

        response = {
            "time_taken": round(time_taken.total_seconds(), 2),
            "question_id": current_question["id"],
            "question": current_question["question"],
            "answer": answer,
        }

        self.answers.append(response)

        return response


    def set_question(self, question):
        self.current_question = question
        self.question_started_at = datetime.datetime.now()


    def finish(self):

        if self.ended_at is not None:
            return

        self.ended_at = datetime.datetime.now()