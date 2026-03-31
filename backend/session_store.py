import json
from contextlib import contextmanager
from database import get_connection
from queries import GET_HISTORY, INSERT_TURN, DELETE_SESSION, SESSION_EXISTS

MAX_CONTEXT_TURNS = 5

@contextmanager
def db_conn(commit=False):
    conn = get_connection()
    try:
        yield conn
        if commit:
            conn.commit()
    finally:
        conn.close()

def get_history(session_id):
    with db_conn() as conn:
        rows = conn.execute(GET_HISTORY, (session_id, MAX_CONTEXT_TURNS)).fetchall()
    result = []
    for r in reversed(rows):
        entry = dict(r)
        entry["response"] = json.loads(entry["response"]) if entry["response"] else None
        result.append(entry)
    return result

def add_turn(session_id, question, sql, response):
    with db_conn(commit=True) as conn:
        conn.execute(
            INSERT_TURN,
            (session_id, question, sql, json.dumps(response) if isinstance(response, (dict, list)) else response),
        )

def clear_session(session_id):
    with db_conn(commit=True) as conn:
        conn.execute(DELETE_SESSION, (session_id,))

def session_exists(session_id):
    with db_conn() as conn:
        return conn.execute(SESSION_EXISTS, (session_id,)).fetchone() is not None
