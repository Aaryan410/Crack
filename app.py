from backend.engine.interview_engine import InterviewEngine
from backend.session.interview import InterviewSession
from backend.ai.evaluator import evaluate, evaluate_report
from backend.store import session_store
from flask import Flask, render_template, request, redirect, session as flask_session
from dotenv import load_dotenv
import os
import time
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

def get_current_interview():

    id = flask_session.get("interview")
    return session_store.load_interview(id)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/start", methods = ["GET", "POST"])
def start():
    if request.method == "GET":
        return redirect("/")

    role = request.form.get("role")

    if not role:
        return redirect("/")

    engine = InterviewEngine(role)
    session = InterviewSession(role)
    session.start()

    flask_session["interview_started_at"] = time.time()

    question = engine.get_next_question()
    session.set_question(question)

    id = str(uuid.uuid4())
    flask_session["interview"] = id
    session_store.save_interview(id, engine, session)

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

    interview_id = flask_session.get("interview")

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
        session_store.save_interview(interview_id, engine, session)
        return redirect("/evaluating")

    next_question = engine.get_next_question()

    if next_question is None:
        started_at = flask_session.get("interview_started_at")

        if started_at is not None:
            flask_session["interview_duration"] = int(time.time() - started_at)

        session.finish()
        session_store.save_interview(interview_id, engine, session)
        return redirect("/report")

    session.set_question(next_question)
    session_store.save_interview(interview_id, engine, session)

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
    interview_id = flask_session.get("interview")

    if engine is None or session is None:
        return redirect("/")

    if session.report is None:
        session.report = evaluate_report(session)
        session_store.save_interview(interview_id, engine, session)

    return render_template("evaluating.html")


@app.route("/report")
def report():

    engine, session = get_current_interview()

    duration = flask_session.get("interview_duration", 0)

    if session is None or session.report is None:
        return redirect("/evaluating")

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