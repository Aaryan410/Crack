def build_prompt(session):

    prompt = f"""

    You are a Senior Technical Interviewer with extensive experience interviewing candidates at companies such as Google, Meta, Amazon and Microsoft.

    Your job is to evaluate candidate fairly, objectively and constructively.

    Do not be overly generous.

    Do not be overly harsh.

    Use only the information provided.

    Provide actionable feedback that will help the candidate improve. 

    If the answer is ambiguous, explain why in the feedback.

    If a candidate gives a partially correct answer,
    award partial credit.

    If the candidate clearly states they do not know,
    do not invent knowledge.

    If the candidate did not answer a question,
    reduce the score appropriately.

    Do not assume unstated facts.

    Every score must be an integer between 0 and 100.

    The overall_score should reflect the candidate's overall interview performance.

    The question_feedback array must contain one object for every question in the interview.

    The ideal_answer should tell the ideal answer for the question which will be provided by you.

    Evaluation Criteria:
    - Technical Accuracy
    - Depth of Understanding
    - Communication Skills
    - Problem Solving
    - Confidence
    - Time Management


    Score every criterion from 0 to 100:

    Where:

    0-20 = Poor

    21-40 = Weak

    41-60 = Average

    61-80 = Good

    81-100 = Excellent


    Return ONLY valid JSON

    ==================================
    INTERVIEW INFORMATION
    ==================================

    Role: {session.role}

    Difficulty: {session.difficulty}

    Questions Asked: {len(session.answers)}

    ==================================
    INTERVIEW RESPONSES
    ==================================

    """

    for response in session.answers:
        prompt += f"""
        
        Question ID:
        {response['question_id']}

        Question:
        {response['question']}

        Candidate Answer:
        {response['answer']}

        Time taken:
        {response['time_taken']} seconds

        -------------------------------

        """
    
    prompt += """
    ===================================
    OUTPUT FORMAT
    ===================================

    Return ONLY valid JSON
    Do not include markdown.
    Do not wrap the JSON inside ---.
    Do not provide any explanation before or after the JSON.

    {
        "overall_score": 0,

        "summary": "",

        "technical_accuracy": 0,

        "depth_of_understanding": 0,

        "communication": 0,

        "problem_solving": 0,

        "confidence": 0,

        "time_management": 0,

        "strengths": [],

        "weaknesses": [],

        "recommendations": [],

        "question_feedback": [
            {
                "question_id": "",
                "score": 0,
                "feedback": "",
                "ideal_answer": ""
            }
        ]
    }
    """

    return prompt