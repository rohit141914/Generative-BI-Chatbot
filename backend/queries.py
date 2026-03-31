GET_HISTORY = """
    SELECT question, sql, response FROM chat_history
    WHERE session_id = ? ORDER BY id DESC LIMIT ?
"""

INSERT_TURN = """
    INSERT INTO chat_history (session_id, question, sql, response) VALUES (?, ?, ?, ?)
"""

DELETE_SESSION = """
    DELETE FROM chat_history WHERE session_id = ?
"""

SESSION_EXISTS = """
    SELECT 1 FROM chat_history WHERE session_id = ? LIMIT 1
"""
