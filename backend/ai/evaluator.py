from prompt.builder import build_prompt
from ai.client import send_prompt
import json

def evaluate(session): 

    candidate_response = session.answers[-1]

    prompt = build_prompt(
        candidate_response,
        session.role,
        session.difficulty
        )

    llm_response = send_prompt(prompt)

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