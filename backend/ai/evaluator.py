from backend.prompt.builder import build_prompt, build_report_prompt
from backend.ai.client import send_prompt
import json

def evaluate(session): 

    candidate_response = session.answers[-1]

    prompt = build_prompt(
        candidate_response,
        session.role,
        session.difficulty
        )

    llm_response = send_prompt(prompt)

    llm_response = llm_response.replace("```json", "")
    llm_response = llm_response.replace("```", "")
    llm_response = llm_response.strip()

    try:

        evaluation = json.loads(llm_response)

        candidate_response["score"] = evaluation["score"]
        candidate_response["feedback"] = evaluation["feedback"]

        if "ideal_answer_summary" in evaluation:
            candidate_response["ideal_answer_summary"] = evaluation["ideal_answer_summary"]

        return evaluation

    except json.JSONDecodeError as e:
        print("Invalid JSON received from Claude:")
        print(e)
        return None


def evaluate_report(session):

    scored_answers = [a for a in session.answers if "score" in a]

    if not scored_answers:
        overall_score = 0
    else:
        overall_score = round (
            sum(answer["score"] for answer in session.answers) /
            len(session.answers)
        )

    prompt = build_report_prompt(session)

    llm_response = send_prompt(prompt)

    llm_response = llm_response.replace("```json", "")
    llm_response = llm_response.replace("```", "")
    llm_response = llm_response.strip()

    report = json.loads(llm_response)

    report["overall_score"] = overall_score

    return report