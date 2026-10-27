import re

from psycopg.errors import UniqueViolation

from backend.security import hash_password, verify_password
from backend.store.postgres import get_db_connection

_DUMMY_PASSWORD_HASH = hash_password("unused-account-password")

def create_account(username, password):
    username = username.strip().lower()

    if not re.fullmatch(r"[a-z0-9_]{3,30}", username):
        raise ValueError("Username must contain 3-30 letters, numbers, or underscores.")

    if not 8 <= len(password) <= 128:
        raise ValueError("Password must contain 8-128 characters.")

    password_hash = hash_password(password)

    try:
        with get_db_connection() as connection: 
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    insert into private.accounts (
                        username,
                        password_hash
                    )
                    values (%s, %s)
                    returning id, username, created_at
                    """,
                    (username, password_hash),
                )

                account = cursor.fetchone()

    except UniqueViolation as error:
        if error.diag.constraint_name == "accounts_username_unique":
            raise ValueError(
                "That username is already taken."
            ) from None

        raise

    return account


def authenticate_account(username, password):
    username = username.strip().lower()

    if not re.fullmatch(r"[a-z0-9_]{3,30}", username):
        return None

    if not 8 <= len(password) <= 128:
        return None

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select id, username, password_hash
                from private.accounts
                where username = %s
                """,
                (username,),
            )

            account  = cursor.fetchone()

    stored_hash = (
        account["password_hash"]
        if account is not None
        else _DUMMY_PASSWORD_HASH
    )

    password_matches = verify_password(stored_hash, password)

    if account is None or not password_matches:
        return None

    return {
        "id": str(account["id"]),
        "username": account["username"],
    }