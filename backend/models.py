from pydantic import BaseModel

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
