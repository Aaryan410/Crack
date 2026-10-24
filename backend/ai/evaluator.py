from backend.prompt.builder import build_prompt, build_report_prompt
from backend.ai.client import send_prompt
from openai import APIError
import json

def evaluate(session): 

    candidate_response = session.answers[-1]

    prompt = build_prompt(
        candidate_response,
        session.role,
        session.difficulty
        )

    try:

        llm_response = send_prompt(prompt)

        if not isinstance(llm_response, str) or not llm_response.strip():
                raise ValueError("AI returned no evaluation text")

        llm_response = llm_response.replace("```json", "")
        llm_response = llm_response.replace("```", "")
        llm_response = llm_response.strip()

        evaluation = json.loads(llm_response)

        if not isinstance(evaluation, dict):
            raise ValueError("Evaluation must be a JSON object")

        score = evaluation.get("score")
        feedback = evaluation.get("feedback")
        ideal_summary = evaluation.get("ideal_answer_summary")

        if type(score) is not int or not 0 <= score <= 100:
            raise ValueError("Score must be an integer from 0 to 100")

        if not isinstance(feedback, str) or not feedback.strip():
            raise ValueError("Feedback must be non-empty text")

        if ideal_summary is not None and not isinstance(ideal_summary, str):
            raise ValueError("Ideal answer summary must be text")

        candidate_response["score"] = score
        candidate_response["feedback"] = feedback

        if ideal_summary is not None:
            candidate_response["ideal_answer_summary"] = ideal_summary
 
        return evaluation

    except ValueError as e:
        print(f"Invalid AI evaluation: {e}")
        return None

    except APIError as e:
        print(f"AI request failed: {e}")
        return None


def evaluate_report(session):

    scored_answers = [a for a in session.answers if "score" in a]

    if not scored_answers:
        overall_score = None
    else:
        overall_score = round (
            sum(answer["score"] for answer in scored_answers) /
            len(scored_answers)
        )

    prompt = build_report_prompt(session)

    try:
        llm_response = send_prompt(prompt)

        if not isinstance(llm_response, str) or not llm_response.strip():
            raise ValueError("AI returned no report text")

        llm_response = llm_response.replace("```json", "")
        llm_response = llm_response.replace("```", "").strip()

        report = json.loads(llm_response)

        if not isinstance(report, dict):
            raise ValueError("Report must be a JSOn object")

        summary = report.get("summary")

        if not isinstance(summary, str) or not summary.strip():
            raise ValueError("Report summary must be non-empty text")

        metric_fields = (
            "technical_accuracy",
            "depth_of_understanding",
            "communication",
            "problem_solving",
            "confidence",
            "time_management",
        )

        for field in metric_fields:
            value = report.get(field)

            if type(value) not in (int, float) or not 0 <= value <= 100:
                raise ValueError(f"{field} must be a number from 0 to 100")

        for field in ("strengths", "weaknesses", "recommendations"):
            items = report.get(field)

            if not isinstance(items, list):
                raise ValueError(f"{field} must be a list")

            if any (
                not isinstance(item, str) or not item.strip()
                for item in items
            ):
                raise ValueError(f"{field} must contain non-empty text entries")

        report["overall_score"] = overall_score
        return report 

    except ValueError as e:
        print(f"Invalid AI report: {e}")
        return None

    except APIError as e:
        print(f"Report request failed: {e}")
        return None
