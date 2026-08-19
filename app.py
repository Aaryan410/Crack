from backend.engine.interview_engine import InterviewEngine
from backend.session.interview import InterviewSession
from backend.ai.evaluator import evaluate, evaluate_report
from flask import Flask, render_template, request, redirect, session as flask_session

app = Flask(__name__)
app.secret_key = "change-this-to-a-real-secret-before-deploying"

active_interviews = {}

def get_current_interview():
    id = flask_session.get("interview")
    if id is None or id not in active_interviews:
         return None, None
    return active_interviews[id]["engine"], active_interviews[id]["session"]

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/start", methods = ["POST"])
def start():
    import uuid

    role = request.form.get("role")

    engine = InterviewEngine(role)
    session = InterviewSession(role)
    session.start()

    question = engine.get_next_question()
    session.set_question(question)

    id = str(uuid.uuid4())
    flask_session["interview"] = id
    active_interviews[id] = {"engine": engine, "session": session}

    return render_template (
         "interview.html",
         role = role,
         question = question,
         question_number = engine.questions_asked
    )


@app.route("/answer", methods = ["POST"])
def answer():
    engine, session = get_current_interview()

    if engine is None:
        return redirect("/")

    answer_text = request.form.get("answer")
    session.submit_answer(answer_text)
    session.difficulty = engine.current_difficulty
    evaluation = evaluate(session)
    engine.update(evaluation)

    if engine.should_end():
        session.finsih()
        return redirect("/report")

    next_question = engine.get_next_question()

    if next_question is None:
        session.finish()
        return redirect("/report")

    session.set_question(next_question)

    return render_template (
        "interview.html",
        role = session.role,
        question = next_question,
        question_number = engine.questions_asked
    )


@app.route("/report")
def report():
    engine, session = get_current_interview()

    if engine is None:
        return redirect("/")

    report_data = evaluate_report(session)

    return render_template (
        "report.html",
        role = session.role,
        report = report_data,
        questions_answer = engine.questions_asked
    )


if __name__ == "__main__":
    app.run(debug=True)