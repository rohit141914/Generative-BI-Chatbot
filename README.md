# Generative BI Chatbot

A full-stack business intelligence assistant that lets you query a loan portfolio database using plain English. Ask questions, get answers with auto-generated SQL, data tables, and charts — powered by Claude AI.

---

## Demo

> "Show NPA loans by state as a bar chart"
> "Monthly collection trend for 2024"
> "Top 5 states by outstanding value"

---

## Features

- Natural language to SQL using Claude (Haiku)
- Auto-generated bar, line, and pie charts
- Data table with results
- Multi-turn conversation with session memory
- Session persistence via localStorage
- Follow-up question suggestions
- Dark theme UI

---

## Tech Stack

| Layer     | Tech                          |
|-----------|-------------------------------|
| Frontend  | React 19, Vite, Axios         |
| Backend   | FastAPI, Python 3.11          |
| Database  | SQLite                        |
| AI        | Anthropic Claude (Haiku)      |
| Charts    | Matplotlib                    |
| Server    | nginx (static files + API proxy)      |
| Deploy    | Vercel (frontend), Render (backend) |

---

## Project Structure

```
chat/
├── backend/
│   ├── main.py              # FastAPI app, routes
│   ├── models.py            # Pydantic request/response models
│   ├── database.py          # SQLite connection, schema
│   ├── session_store.py     # In-memory session/history store
│   ├── sql_executor.py      # SQL safety check + execution
│   ├── chart_renderer.py    # Matplotlib chart generation
│   ├── helpers.py           # Answer text + follow-up suggestions
│   ├── seed_data.py         # Database seeding script
│   ├── llm/
│   │   ├── llm_caller.py    # Anthropic API call + retry logic
│   │   └── prompt_builder.py# System prompt + user message builder
│   ├── requirements.txt
│   └── Dockerfile
├── Frontend/
│   ├── src/
│   │   ├── App.jsx          # Main app, chat logic
│   │   ├── App.css          # Dark theme styles
│   │   ├── constants.js     # API base URL, sample questions
│   │   ├── api.js           # Axios API functions
│   │   ├── endpoints.js     # URL constants
│   │   └── components/
│   │       ├── AssistantMessage.jsx
│   │       ├── DataTable.jsx
│   │       └── SqlBlock.jsx
│   ├── nginx.conf           # Serves static files + proxies API to backend
│   ├── vercel.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Anthropic API key

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:
```
ANTHROPIC_API_KEY=your_key_here
```

Seed the database:
```bash
python seed_data.py
```

Start the server:
```bash
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`

### Frontend

```bash
cd Frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` — Vite proxies API calls to the backend automatically.

---

## Docker

```bash
docker compose up --build
```

- Frontend → `http://localhost` (served by nginx)
- Backend → `http://localhost:8000`

nginx serves the React build as static files and proxies all API routes (`/chat`, `/sessions`, `/schema`, `/outputs`, `/health`) to the FastAPI backend container. This replaces the Vite dev proxy used in local development.

---

## Deployment

### Backend (Render)
1. Create a new **Web Service** on [Render](https://render.com)
2. Set **Root Directory** to `backend`
3. Set **Start Command** to `uvicorn main:app --host 0.0.0.0 --port 8000`
4. Add environment variable: `ANTHROPIC_API_KEY=your_key`

### Frontend (Vercel)
1. Import repo on [Vercel](https://vercel.com)
2. Set **Root Directory** to `Frontend`
3. Add environment variable: `VITE_API_BASE_URL=https://your-render-app.onrender.com`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Send a question, get SQL + chart + answer |
| `GET` | `/sessions/{id}` | Get session history |
| `DELETE` | `/sessions/{id}` | Clear a session |
| `GET` | `/schema` | Get database schema |
| `GET` | `/health` | Health check |
