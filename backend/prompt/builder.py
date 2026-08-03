def build_prompt(response, role, difficulty):

    prompt = f"""You are a Senior Technical Interviewer evaluating ONE interview answer.

    Role: {role}
    Difficulty: {difficulty}

    Question:
    {response['question']}

    Candidate Answer:
    {response['answer']}

    Time taken: {response['time_taken']} seconds

    Rules:
    - Score 0-100 (integer). Be fair, not generous, not harsh.
    - If the candidate said they don't know, or gave no real answer, score low and do not invent credit.
    - Partial credit for partially correct answers.
    - feedback: 2-3 sentences max. Specific and actionable, not generic.
    - ideal_answer_summary: 1-2 sentences max. A compressed pointer to what a strong answer covers, not a full essay.
    - Do not exceed the length limits above under any circumstance.

    Return ONLY this JSON, no markdown, no commentary, no code fences:

    {{
        "question_id": "{response['question_id']}",
        "score": 0,
        "feedback": "",
        "ideal_answer_summary": ""
    }}
    """

    return prompt


def build_report_prompt(session):

    prompt = f"""You are a Senior Technical Interviewer producing a final interview report.

    You already scored each answer individually. Your job now is to synthesize
    an overall performance summary from those scores - do not re-grade individual answers.

    Based on the above, return ONLY this JSON.

    Rules:

    - Strengths MUST contain only positive aspects.
    - Weaknesses MUST contain only genuine gaps, mistakes, or missed depth - never
      a strength restated, reworded, or copied into the weaknesses list.
    - Before writing the weaknesses array, check each entry against the strengths
      array, If an entry says the same thing as a strength (even reworded), delete
      it from weaknesses.
    - It is CORRECT and EXPECTED for weaknesses to be shorter than  strengths, or
      empty, when the candidate performed well. A strong candidate should often
      have 0-1 weaknesses and 3-4 strengths, Do not pad weaknesses to match the
      length of strengths.
    - If you cannot find a genuine, specific weakness, return an empty list: []    
      Do NOT reuse, copy, or repurpose a strength to fill this list.
    - If the candidate has only minor weaknesses is empty, recommendations may focus on going further/deeper rather
      than fixing a gap.
    - Return valid JSON only.
    

    Role: {session.role}
    Difficulty: {session.difficulty}
    Questions Asked: {len(session.answers)}

    Per-question results:
    """

    for response in session.answers:
        prompt += f"""
            - Question ID: {response['question_id']}
            Score: {response.get('score', 'N/A')}
            Feedback: {response.get('feedback', 'N/A')}
            """

    prompt += """
        Based on the above, return ONLY this JSON, no markdown, no commentary:

        {
            "summary": "",
            "technical_accuracy": 0,
            "depth_of_understanding": 0,
            "communication": 0,
            "problem_solving": 0,
            "confidence": 0,
            "time_management": 0,
            "strengths": [],
            "weaknesses": [],
            "recommendations": []
        }

    Keep summary to 2-3 sentences. Keep each strengths/weaknesses/recommendations
    entry to a single short sentence. Aim for a concise, high-signal report, not
    an exhaustive one. 

    """

    return prompt