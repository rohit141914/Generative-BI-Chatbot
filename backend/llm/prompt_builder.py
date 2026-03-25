from database import DB_SCHEMA

SYSTEM_PROMPT_TEMPLATE = """You are a SQL query generator for a financial NBFC database.
Output ONLY valid SQLite SQL. No explanations, no markdown fences, no comments.
Never use DROP, DELETE, UPDATE, INSERT, or ALTER statements.

Schema:
{schema}

{prior_context}"""

def build_system_prompt(prior_turns):
    if prior_turns:
        lines = []
        for i, turn in enumerate(prior_turns, 1):
            lines.append(f"Turn {i}:")
            lines.append(f"  Question: {turn['question']}")
            lines.append(f"  SQL used: {turn['sql']}")
        prior_context = "Conversation so far (SQL only, no data values):\n" + "\n".join(lines)
    else:
        prior_context = ""
    return SYSTEM_PROMPT_TEMPLATE.format(
        schema=DB_SCHEMA.strip(),
        prior_context=prior_context,
    ).strip()

def build_user_message(question, error_context=""):
    if error_context:
        return (
            f"{question}\n\n"
            f"Previous SQL failed with:\n{error_context}\n"
            f"Please generate a corrected SQL query."
        )
    return question
