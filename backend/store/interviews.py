from backend.store.postgres import get_db_connection

from psycopg.types.json import Jsonb

from datetime import timezone

def save_completed_interview(
    *,
    interview_id,
    account_id,
    role,
    overall_score,
    questions_answered,
    duration_seconds,
    report,
    answers,
):
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                insert into private.interviews (
                    id,
                    account_id,
                    role,
                    overall_score,
                    questions_answered,
                    duration_seconds,
                    report,
                    answers
                )
                values (%s, %s, %s, %s, %s, %s, %s, %s)
                on conflict (id) do nothing
                """,
                (
                    interview_id,
                    account_id,
                    role,
                    overall_score,
                    questions_answered,
                    duration_seconds,
                    Jsonb(report),
                    Jsonb(answers),
                ),
            )


def get_dashboard_data(account_id):
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """ 
                select 
                    count(*) as completed,
                    round(avg(overall_score), 1) as average,
                    max(overall_score) as best
                from private.interviews
                where account_id = %s
                """,
                (account_id,),
            )

            summary = cursor.fetchone()

            cursor.execute(
                """
                select
                    id,
                    role,
                    overall_score,
                    questions_answered,
                    duration_seconds,
                    completed_at
                from private.interviews
                where account_id = %s
                order by completed_at desc, id desc
                limit 10
                """,
                (account_id,),
            )

            rows = cursor.fetchall()

    stats = {
        "completed": summary["completed"],
        "average": (
            float(summary["average"])
            if summary["average"] is not None
            else None
        ),
        "best": (
            float(summary["best"])
            if summary["best"] is not None
            else None
        ),
    }

    interviews = []

    for row in rows:
        item = dict(row)

        item["overall_score"] = float(item["overall_score"])

        item["role_label"] = (
            item["role"]
            .replace("-", " ")
            .title()
            .replace("Ai", "AI")
            .replace("Ml", "ML")
        )

        minutes, seconds = divmod(item["duration_seconds"], 60) 
        item["duration_label"] = f"{minutes}:{seconds:02d}"

        completed_at = item["completed_at"].astimezone(timezone.utc)
        item["completed_label"] = completed_at.strftime(
            "%d %b %Y, %H:%M"
        )

        interviews.append(item)

    chronological = list(reversed(interviews))
    chart_points = []

    for index, interview in enumerate(chronological):
        if len(chronological) == 1:
            x = 332
        else:
            x = 48 + index * 558 / (len(chronological) - 1)

        y = 200 - interview["overall_score"] / 100 * 176

        chart_points.append(
            {
                "x": round(x, 2),
                "y": round(y, 2),
                "number": index + 1,
                "score": interview["overall_score"],
                "role": interview["role_label"],
            }
        )

    chart_line = " ".join(
        f"{point['x']},{point['y']}"
        for point in chart_points
    )

    return {
        "stats": stats,
        "interviews": interviews,
        "chart_points": chart_points,
        "chart_line": chart_line,
    }