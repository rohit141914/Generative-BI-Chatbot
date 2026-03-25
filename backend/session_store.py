from collections import defaultdict

MAX_CONTEXT_TURNS  = 5
_sessions = defaultdict(list)

def get_history(session_id):
    return list(_sessions[session_id])

def add_turn(session_id, question, sql, response):
    turns = _sessions[session_id]
    turns.append({"question": question, "sql": sql, "response": response})
    _sessions[session_id] = turns[-MAX_CONTEXT_TURNS :]

def clear_session(session_id):
    _sessions.pop(session_id, None)

def session_exists(session_id):
    return session_id in _sessions