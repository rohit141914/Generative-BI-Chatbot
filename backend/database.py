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
CREATE TABLE IF NOT EXISTS chat_history (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT    NOT NULL,
    question   TEXT,
    sql        TEXT,
    response   TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_chat_history_session ON chat_history(session_id);
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

