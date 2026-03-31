import json
from database import get_connection

MAX_CONTEXT_TURNS = 5

def get_history(session_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT question, sql, response FROM chat_history "
        "WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, MAX_CONTEXT_TURNS),
    ).fetchall()
    conn.close()
    result = []
    for r in reversed(rows):
        entry = dict(r)
        entry["response"] = json.loads(entry["response"]) if entry["response"] else None
        result.append(entry)
    return result

def add_turn(session_id, question, sql, response):
    conn = get_connection()
    conn.execute(
        "INSERT INTO chat_history (session_id, question, sql, response) VALUES (?, ?, ?, ?)",
        (session_id, question, sql, json.dumps(response) if isinstance(response, (dict, list)) else response),
    )
    conn.commit()
    conn.close()

def clear_session(session_id):
    conn = get_connection()
    conn.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

def session_exists(session_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM chat_history WHERE session_id = ? LIMIT 1", (session_id,)
    ).fetchone()
    conn.close()
    return row is not None
