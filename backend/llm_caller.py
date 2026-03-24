import os, re
import anthropic
from prompt_builder import build_system_prompt, build_user_message
from sql_executor import execute_sql, SQLSafetyError

MAX_RETRIES = 2
# MODEL = "claude-sonnet-4-20250514"
MODEL = "claude-haiku-4-5-20251001"
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def _strip_sql(raw):
    raw = raw.strip()
    raw = re.sub(r"^```(?:sql)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()

def generate_and_execute_sql(question, prior_turns):
    system_prompt = build_system_prompt(prior_turns)
    error_context = ""
    for attempt in range(MAX_RETRIES + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=512,
            system=system_prompt,
            messages=[{"role": "user", "content": build_user_message(question, error_context)}],
        )
        sql = _strip_sql(response.content[0].text)
        try:
            rows = execute_sql(sql)
            return sql, rows
        except SQLSafetyError:
            raise
        except Exception as e:
            error_context = str(e)
            if attempt == MAX_RETRIES:
                raise RuntimeError(f"SQL failed after {MAX_RETRIES+1} attempts: {error_context}") from e
