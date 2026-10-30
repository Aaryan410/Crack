from backend.store.postgres import get_db_connection

def save_completed_interview(
    *,
    interview_id,
    account_id,
    role,
    overall_score,
    questions_answered,
    duration_seconds,
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
                    duration_seconds
                )
                values (%s, %s, %s, %s, %s, %s)
                on conflict (id) do nothing
                """,
                (
                    interview_id,
                    account_id,
                    role,
                    overall_score,
                    questions_answered,
                    duration_seconds,
                ),
            )