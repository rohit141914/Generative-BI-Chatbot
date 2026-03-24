import re
import sqlite3
from database import get_connection

FORBIDDEN_PATTERN = re.compile(
    r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE|REPLACE|CREATE|ATTACH|DETACH)\b",
    re.IGNORECASE,
)

class SQLSafetyError(Exception):
    pass

def check_safety(sql):
    match = FORBIDDEN_PATTERN.search(sql)
    if match:
        raise SQLSafetyError(
            f"SQL contains forbidden operation '{match.group().upper()}'. "
            "Only SELECT queries are allowed."
        )

def execute_sql(sql):
    check_safety(sql)
    conn = get_connection()
    try:
        cursor = conn.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows
    finally:
        conn.close()
