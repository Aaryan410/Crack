from backend.engine.interview_engine import InterviewEngine
from backend.session.interview import InterviewSession
from backend.ai.evaluator import evaluate, evaluate_report
from backend.store import session_store
from backend.store.accounts import create_account, authenticate_account
from backend.store.interviews import (save_completed_interview, get_dashboard_data)
from flask import Flask, render_template, request, redirect, session as flask_session, jsonify, abort, flash, url_for
from dotenv import load_dotenv
from psycopg import Error as DatabaseError
from functools import wraps
import secrets
import os
import time
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

def get_current_interview():

    id = flask_session.get("interview")
    return session_store.load_interview(id)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not flask_session.get("user_id"):
            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped_view

@app.route("/")
def home():
    if not flask_session.get("user_id"):
        return redirect(url_for("login"))

    return redirect(url_for("dashboard"))


@app.route("/practice")
@login_required
def practice():
    return render_template("index.html")


@app.route("/start", methods = ["GET", "POST"])
@login_required
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
@login_required
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
        return redirect("/evaluating")

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
@login_required
def evaluating():
    engine, session = get_current_interview()

    if engine is None or session is None:
        return redirect("/")

    return render_template("evaluating.html")


@app.route("/report")
@login_required
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


@app.route("/generate-report", methods = ["POST"])
def generate_report():
    account_id = flask_session.get("user_id")

    if not account_id:
        return jsonify(error = "Please log in again."), 401

    engine, session = get_current_interview()
    interview_id = flask_session.get("interview")

    if engine is None or session is None:
        return jsonify(error = "Your interview has expired."), 410

    if session.started_at is None or session.ended_at is None:
        return jsonify(error = "The interview has not finished yet."), 409

    if session.report is None:
        report_data = evaluate_report(session)

        if report_data is None:
            return jsonify(
                error = "We couldn't generate your report. Please try again."
            ), 503

        session.report = report_data
        session_store.save_interview(interview_id, engine, session)


    if not isinstance(session.report, dict):
        return jsonify(
            error = "The generated report has an invalid format."
        ), 503

    overall_score = session.report.get("overall_score")

    if (
        type(overall_score) not in (int, float)
        or not 0 <= overall_score <= 100
    ):
        return jsonify(
            error = "This interview has no valid overall score to save."
        ), 503

    duration_seconds = max(
        0,
        int((session.ended_at - session.started_at).total_seconds()),
    )

    try:
        save_completed_interview(
            interview_id = interview_id,
            account_id = account_id,
            role = session.role,
            overall_score = overall_score,
            questions_answered = len(session.answers),
            duration_seconds = duration_seconds,
            report = session.report,
            answers = session.answers,
        )
    except DatabaseError:
        app.logger.exception("Saving completed interview failed")

        return jsonify(
            error = "Your report was generated, but saving it failed. Please retry."
        ), 503

    return jsonify(redirect_url = "/report")


@app.route("/dashboard")
@login_required
def dashboard():
    dashboard_error = None
    status = 200

    try:
        data = get_dashboard_data(
            flask_session["user_id"]
        )

    except DatabaseError:
        app.logger.exception("Loading dashboard failed")

        dashboard_error = (
            "We couldn't load your interview history. Please try again."
        )

        status = 503

        data = {
            "stats": {
                "completed": None,
                "average": None,
                "best": None,
            },
            "interview": [],
            "chart_points": [],
            "chart_line": "",
        }

    return render_template(
        "dashboard.html",
        dashboard_error = dashboard_error,
        **data,
    ), status


@app.route("/signup", methods = ["GET", "POST"])
def signup():
    csrf_token = flask_session.get("csrf_token")

    if csrf_token is None:
        csrf_token = secrets.token_urlsafe(32)
        flask_session["csrf_token"] = csrf_token

    username = ""
    error = None
    status = 200

    if request.method == "POST":
        submitted_token = request.form.get("csrf_token", "")

        if not secrets.compare_digest(
            submitted_token.encode("utf-8"),
            csrf_token.encode("utf-8"),
        ): 
            abort(400, description = "Invalid form submission. Reload and try again.")

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        try:
            create_account(username, password)

        except ValueError as exc:
            error = str(exc)
            status = 400

        except DatabaseError:
            app.logger.exception("Account creation failed")
            error = "We couldn't create your account. Please try again."
            status = 503

        else:
            flash("Your account was created successfully. Please log in")
            return redirect(url_for("login"))

    return render_template (
        "signup.html",
        csrf_token = csrf_token,
        username = username,
        error = error,
    ), status


@app.route("/login", methods = ["GET", "POST"])
def login():
    csrf_token = flask_session.get("csrf_token")

    if csrf_token is None:
        csrf_token = secrets.token_urlsafe(32)
        flask_session["csrf_token"] = csrf_token

    username = ""
    error = None
    status = 200

    if request.method == "POST":
        submitted_token = request.form.get("csrf_token", "")

        if not secrets.compare_digest(
            submitted_token.encode("utf-8"),
            csrf_token.encode("utf-8"),
        ): 
            abort(
                400,
                description = "Invalid from submission. Reload and try again.",
            )

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        try:
            account = authenticate_account(username, password)

        except DatabaseError:
            app.logger.exception("Login failed")
            error = "We couldn't sign you in. Please try again."
            status = 503

        else:
            if account is None:
                error = "Incorrect username or password."
                status = 401

            else:
                flask_session.clear()
                flask_session["user_id"] = account["id"]
                flask_session["username"] = account["username"]
                flask_session["csrf_token"] = secrets.token_urlsafe(32)

                return redirect(url_for("dashboard"))

    return render_template(
        "login.html",
        csrf_token = csrf_token,
        username = username,
        error = error,
    ), status


@app.route("/logout", methods = ["POST"])
@login_required
def logout():
    csrf_token = flask_session.get("csrf_token", "")
    submitted_token = request.form.get("csrf_token", "")

    if not csrf_token or not secrets.compare_digest(
        submitted_token.encode("utf-8"),
        csrf_token.encode("utf-8"),
    ): 
        abort(
            400,
            description = "Invalid form submission. Reload and try again.",
        )

    flask_session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run()