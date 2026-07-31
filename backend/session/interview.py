import datetime


class InterviewSession:

    def __init__(self, role, difficulty, questions):
        self.role = role
        self.difficulty = difficulty
        self.questions = questions

        self.current_index = 0
        self.answers = []
        self.started_at = None
        self.ended_at = None
        self.question_started_at = None

    def start(self):
        if self.started_at is not None:
            return

        self.started_at = datetime.datetime.now()

    def next_question(self):

        self.question_started_at = datetime.datetime.now()

        if self.current_index == len(self.questions):
            return None
        else:
            return self.questions[self.current_index]


    def submit_answer(self, answer):
        current_question = self.questions[self.current_index]

        current_time = datetime.datetime.now()

        time_taken = current_time - self.question_started_at

        response = {
            "time_taken": round(time_taken.total_seconds(), 2),
            "question_id": current_question["id"],
            "answer": answer,
        }

        self.answers.append(response)

        self.current_index += 1

        return response


    def finish(self):

        if self.ended_at is not None:
            return

        self.ended_at = datetime.datetime.now()