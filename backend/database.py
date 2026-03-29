import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "loans.db")

SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS loans (
    loan_id       TEXT PRIMARY KEY,
    borrower_id   TEXT,
    product_type  TEXT,
    disbursed_date TEXT,
    amount        REAL,
    outstanding   REAL,
    state         TEXT,
    branch_id     TEXT,
    loan_status   TEXT,
    interest_rate REAL,
    tenure_months INTEGER
);
CREATE TABLE IF NOT EXISTS repayments (
    repayment_id TEXT PRIMARY KEY,
    loan_id      TEXT,
    due_date     TEXT,
    paid_date    TEXT,
    amount_due   REAL,
    amount_paid  REAL,
    days_overdue INTEGER
);
CREATE TABLE IF NOT EXISTS borrowers (
    borrower_id TEXT PRIMARY KEY,
    age         INTEGER,
    gender      TEXT,
    occupation  TEXT,
    city_tier   INTEGER,
    state       TEXT
);
CREATE TABLE IF NOT EXISTS query_logs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id    TEXT,
    question      TEXT,
    sql_generated TEXT,
    created_at    TEXT DEFAULT (datetime('now'))
);
"""

DB_SCHEMA = """
Table: loans
  loan_id        TEXT PRIMARY KEY
  borrower_id    TEXT
  product_type   TEXT  -- values: 'personal', 'business', 'gold', 'vehicle'
  disbursed_date TEXT  -- ISO date e.g. '2024-03-15'
  amount         REAL
  outstanding    REAL
  state          TEXT  -- Indian state name
  branch_id      TEXT
  loan_status    TEXT  -- values: 'active', 'closed', 'npa', 'written_off'
  interest_rate  REAL
  tenure_months  INTEGER

Table: repayments
  repayment_id TEXT PRIMARY KEY
  loan_id      TEXT  -- FK -> loans.loan_id
  due_date     TEXT  -- ISO date
  paid_date    TEXT  -- ISO date, NULL if unpaid
  amount_due   REAL
  amount_paid  REAL
  days_overdue INTEGER

Table: borrowers
  borrower_id TEXT PRIMARY KEY
  age         INTEGER
  gender      TEXT    -- 'male', 'female', 'other'
  occupation  TEXT
  city_tier   INTEGER -- 1, 2, or 3
  state       TEXT
"""

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA_DDL)
    conn.commit()
    conn.close()

def save_query_log(session_id: str, question: str, sql_generated: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO query_logs (session_id, question, sql_generated) VALUES (?, ?, ?)",
        (session_id, question, sql_generated),
    )
    conn.commit()
    conn.close()