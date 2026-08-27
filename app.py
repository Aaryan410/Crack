from backend.engine.interview_engine import InterviewEngine
from backend.session.interview import InterviewSession
from backend.ai.evaluator import evaluate, evaluate_report
from flask import Flask, render_template, request, redirect, session as flask_session
from dotenv import load_dotenv
import os
import time

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

active_interviews = {}

def get_current_interview():

    id = flask_session.get("interview")

    if id is None or id not in active_interviews:
        return None, None

    return (active_interviews[id]["engine"], active_interviews[id]["session"])

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

    flask_session["interview_started_at"] = time.time()

    question = engine.get_next_question()
    session.set_question(question)

    id = str(uuid.uuid4())
    flask_session["interview"] = id
    active_interviews[id] = {"engine": engine, "session": session}

    return render_template (
        "interview.html",
        role = role,
        question = question,
        question_number = engine.questions_asked,
        interview_started_at = flask_session["interview_started_at"]
    )


@app.route("/answer", methods = ["POST"])
def answer():
    engine, session = get_current_interview()

    started_at = flask_session.get("interview_started_at")

    if engine is None:
        return redirect("/")

    answer_text = request.form.get("answer")
    session.submit_answer(answer_text)
    session.difficulty = engine.current_difficulty
    evaluation = evaluate(session)
    engine.update(evaluation)

    if engine.should_end():
        started_at = flask_session.get("interview_started_at")

        if started_at is not None:
            flask_session["interview_duration"] = int(time.time() - started_at)

        session.finish()
        return redirect("/evaluating")

    next_question = engine.get_next_question()

    if next_question is None:
        started_at = flask_session.get("interview_started_at")

        if started_at is not None:
            flask_session["interview_duration"] = int(time.time() - started_at)

        session.finish()
        return redirect("/report")

    session.set_question(next_question)

    return render_template (
        "interview.html",
        role = session.role,
        question = next_question,
        question_number = engine.questions_asked,
        interview_started_at = flask_session["interview_started_at"]
    )


@app.route("/evaluating", methods = ["GET"])
def evaluating():
    engine, session = get_current_interview()

    if engine is None or session is None:
        return redirect("/")

    if session.report is None:
        session.report = evaluate_report(session)

    return render_template("evaluating.html")


@app.route("/report")
def report():

    engine, session = get_current_interview()

    duration = flask_session.get("interview_duration", 0)

    print("ENGINE:", engine)
    print("SESSION:", session)

    if session.report is None:
        return redirect("/evaluting")

    if engine is None:
        return redirect("/")

    report_data = session.report

    display_role = session.role.replace("_", " ").title()
    display_role = display_role.replace("Ai", "AI").replace("Ml", "ML")

    return render_template (
        "report.html",
        role = display_role,
        report = report_data,
        questions_answered = engine.questions_asked,
        answers = session.answers,
        duration = duration
    )


if __name__ == "__main__":
    app.run()