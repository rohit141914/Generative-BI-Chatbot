import os, uuid
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from database import init_db, SCHEMA_FOR_LLM
from session_store import get_history, add_turn, clear_session, session_exists
from llm_caller import generate_and_execute_sql
from sql_executor import SQLSafetyError
from chart_renderer import render_chart

app = FastAPI(title="BI Chatbot")

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5173"],
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

@app.on_event("startup")
def startup():
    init_db()

class ChatRequest(BaseModel):
    session_id: str | None = None
    question: str

class ChatResponse(BaseModel):
    session_id: str
    question: str
    sql_generated: str
    chart_type: str
    chart_url: str
    table_data: list[dict]
    answer_text: str
    follow_up_suggestions: list[str]

def _answer_text(rows):
    if not rows:
        return "No results found."
    cols = list(rows[0].keys())
    label_col = cols[0]
    value_col = cols[1] if len(cols) > 1 else None
    if value_col:
        top = rows[0]
        try:
            val = f"{float(top[value_col]):,.2f}"
        except:
            val = str(top[value_col])
        return f"{top[label_col]} has the highest {value_col} ({val}) across {len(rows)} result(s)."
    return f"Query returned {len(rows)} result(s)."

def _suggestions(question):
    q = question.lower()
    tips = []
    if "state" in q:
        tips.append("Break this down by product type")
    if "trend" not in q:
        tips.append("Show the monthly trend for 2024")
    if "npa" not in q:
        tips.append("Filter for NPA loans only")
    return tips[:3]

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id or f"sess-{uuid.uuid4().hex[:8]}"
    prior_turns = get_history(session_id)
    try:
        sql, rows = generate_and_execute_sql(req.question, prior_turns)
    except SQLSafetyError as e:
        raise HTTPException(status_code=400, detail={"error": "safety_guard", "message": str(e)})
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail={"error": "llm_error", "message": str(e)})

    chart_type, chart_url = render_chart(rows, session_id)
    answer_text = _answer_text(rows)
    follow_up_suggestions = _suggestions(req.question)

    add_turn(session_id, req.question, sql, {
        "sql_generated": sql,
        "chart_type": chart_type,
        "chart_url": chart_url,
        "table_data": rows[:100],
        "answer_text": answer_text,
        "follow_up_suggestions": follow_up_suggestions,
    })

    return ChatResponse(
        session_id=session_id,
        question=req.question,
        sql_generated=sql,
        chart_type=chart_type,
        chart_url=chart_url,
        table_data=rows[:100],
        answer_text=answer_text,
        follow_up_suggestions=follow_up_suggestions,
    )

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "history": get_history(session_id)}

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    clear_session(session_id)
    return {"message": f"Session {session_id} cleared"}

@app.get("/schema")
async def get_schema():
    return {"schema": SCHEMA_FOR_LLM}

@app.get("/health")
async def health():
    return {"status": "ok"}
