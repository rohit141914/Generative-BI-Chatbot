import os, uuid
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import init_db, SCHEMA_FOR_LLM
from session_store import get_history, add_turn, clear_session, session_exists
from llm.llm_caller import generate_and_execute_sql
from sql_executor import SQLSafetyError
from chart_renderer import render_chart
from helpers import answer_text, suggestions
from models import ChatRequest, ChatResponse

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
    ans_text = answer_text(rows)
    follow_up_suggestions = suggestions(req.question)

    add_turn(session_id, req.question, sql, {
        "sql_generated": sql,
        "chart_type": chart_type,
        "chart_url": chart_url,
        "table_data": rows[:100],
        "answer_text": ans_text,
        "follow_up_suggestions": follow_up_suggestions,
    })

    return ChatResponse(
        session_id=session_id,
        question=req.question,
        sql_generated=sql,
        chart_type=chart_type,
        chart_url=chart_url,
        table_data=rows[:100],
        answer_text=ans_text,
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
