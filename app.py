from backend.engine.interview_engine import InterviewEngine
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/start", methods = ["POST"])
def start():
    role = request.form.get("role")
    engine = InterviewEngine(role)
    question = engine.get_next_question()

    return render_template(
        "interview.html",
        role = role,
        question = question["question"],
        question_number = 1
    )

if __name__ == "__main__":
    app.run(debug=True)