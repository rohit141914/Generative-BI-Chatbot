import { useState, useRef, useEffect } from 'react'

const API_BASE = ''  // empty string because Vite proxy handles it

const styles = {
  app: {
    display: 'flex', flexDirection: 'column', height: '100vh', background: '#f0f2f5',
  },
  header: {
    background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
    color: '#fff', padding: '14px 24px',
    display: 'flex', alignItems: 'center', gap: 12,
    boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
  },
  headerTitle: { fontSize: 18, fontWeight: 600, letterSpacing: 0.3 },
  headerSub: { fontSize: 12, opacity: 0.6, marginTop: 2 },
  sessionBadge: {
    marginLeft: 'auto', fontSize: 11, background: 'rgba(255,255,255,0.12)',
    padding: '3px 10px', borderRadius: 20, fontFamily: 'monospace',
  },
  chatArea: {
    flex: 1, overflowY: 'auto', padding: '20px 16px',
    display: 'flex', flexDirection: 'column', gap: 16,
  },
  emptyState: {
    display: 'flex', flexDirection: 'column', alignItems: 'center',
    justifyContent: 'center', flex: 1, gap: 16, opacity: 0.8, paddingBottom: 60,
  },
  emptyIcon: { fontSize: 48 },
  emptyTitle: { fontSize: 20, fontWeight: 600, color: '#333' },
  emptyDesc: { fontSize: 14, color: '#777', textAlign: 'center', maxWidth: 380 },
  sampleGrid: {
    display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 8, maxWidth: 480,
  },
  sampleBtn: {
    background: '#fff', border: '1px solid #dde1e7', borderRadius: 10,
    padding: '10px 12px', fontSize: 12, color: '#444', cursor: 'pointer',
    textAlign: 'left', lineHeight: 1.4,
  },
  userBubble: {
    alignSelf: 'flex-end', background: '#4A7FD4', color: '#fff',
    padding: '10px 16px', borderRadius: '18px 18px 4px 18px',
    maxWidth: '60%', fontSize: 14, lineHeight: 1.5,
  },
  assistantCard: {
    alignSelf: 'flex-start', background: '#fff', borderRadius: 16,
    padding: '16px 18px', maxWidth: '90%', width: '100%',
    boxShadow: '0 1px 4px rgba(0,0,0,0.08)', border: '1px solid #e8eaed',
  },
  answerText: { fontSize: 14, color: '#222', lineHeight: 1.6, marginBottom: 12 },
  sqlToggle: {
    background: 'none', border: 'none', cursor: 'pointer',
    color: '#4A7FD4', fontSize: 12, padding: 0, marginBottom: 6,
  },
  sqlBlock: {
    background: '#1e1e2e', color: '#a8d8a8', borderRadius: 8,
    padding: '10px 14px', fontSize: 12, fontFamily: 'monospace',
    overflowX: 'auto', marginBottom: 12, lineHeight: 1.6,
  },
  chartImg: {
    width: '100%', borderRadius: 10, marginBottom: 12, border: '1px solid #eee',
  },
  tableWrap: { overflowX: 'auto', marginBottom: 12 },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: 13 },
  th: {
    background: '#f5f7fa', padding: '8px 12px', textAlign: 'left',
    fontSize: 12, fontWeight: 600, color: '#555', borderBottom: '2px solid #e0e0e0',
  },
  td: { padding: '7px 12px', borderBottom: '1px solid #f0f0f0', color: '#333' },
  followUps: { display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 },
  followUpLabel: { fontSize: 11, color: '#aaa', marginBottom: 4 },
  followUpBtn: {
    background: '#f0f4ff', border: '1px solid #c5d3f8', color: '#3a62c0',
    borderRadius: 20, padding: '5px 12px', fontSize: 12, cursor: 'pointer',
  },
  errorCard: {
    alignSelf: 'flex-start', background: '#fff5f5', border: '1px solid #fecaca',
    borderRadius: 12, padding: '12px 16px', maxWidth: '70%',
    fontSize: 13, color: '#c0392b',
  },
  loadingBubble: {
    alignSelf: 'flex-start', background: '#fff', border: '1px solid #e8eaed',
    borderRadius: 18, padding: '12px 20px', fontSize: 13, color: '#666',
    boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
  },
  inputArea: {
    background: '#fff', borderTop: '1px solid #e0e0e0',
    padding: '12px 16px', display: 'flex', gap: 8, alignItems: 'flex-end',
  },
  textarea: {
    flex: 1, border: '1.5px solid #dde1e7', borderRadius: 24,
    padding: '10px 18px', fontSize: 14, outline: 'none',
    resize: 'none', fontFamily: 'inherit', lineHeight: 1.5,
    maxHeight: 120, minHeight: 42,
  },
  sendBtn: {
    background: '#4A7FD4', color: '#fff', border: 'none',
    borderRadius: 24, padding: '10px 22px', fontSize: 14,
    cursor: 'pointer', fontWeight: 500, height: 42, whiteSpace: 'nowrap',
  },
  sendBtnDisabled: { background: '#b0c4e8', cursor: 'not-allowed' },
  clearBtn: {
    background: 'transparent', border: '1px solid #dde1e7', color: '#888',
    borderRadius: 24, padding: '10px 16px', fontSize: 13, cursor: 'pointer', height: 42,
  },
}

const SAMPLE_QUESTIONS = [
  'Total disbursement by product type',
  'Monthly collection trend for 2024',
  'Top 5 states by outstanding value',
  'NPA rate (%) by branch',
  'Avg interest rate: gold vs personal',
  'Show NPA loans by state as a bar chart',
]

function SqlBlock({ sql }) {
  const [show, setShow] = useState(false)
  return (
    <div>
      <button style={styles.sqlToggle} onClick={() => setShow(v => !v)}>
        {show ? '▾ Hide SQL' : '▸ View generated SQL'}
      </button>
      {show && <pre style={styles.sqlBlock}>{sql}</pre>}
    </div>
  )
}

function DataTable({ rows }) {
  if (!rows || rows.length === 0) return null
  const cols = Object.keys(rows[0])
  return (
    <div style={styles.tableWrap}>
      <table style={styles.table}>
        <thead>
          <tr>{cols.map(c => <th key={c} style={styles.th}>{c}</th>)}</tr>
        </thead>
        <tbody>
          {rows.slice(0, 20).map((row, i) => (
            <tr key={i} style={{ background: i % 2 === 0 ? '#fff' : '#fafafa' }}>
              {cols.map(c => (
                <td key={c} style={styles.td}>
                  {typeof row[c] === 'number'
                    ? Number(row[c]).toLocaleString('en-IN')
                    : row[c] ?? '—'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length > 20 && (
        <div style={{ fontSize: 12, color: '#999', marginTop: 6, paddingLeft: 4 }}>
          Showing 20 of {rows.length} rows
        </div>
      )}
    </div>
  )
}

function AssistantMessage({ msg, onFollowUp }) {
  return (
    <div style={styles.assistantCard}>
      <p style={styles.answerText}>{msg.answer_text}</p>

      {msg.chart_url && (
        <img
          src={`${API_BASE}${msg.chart_url}`}
          alt="chart"
          style={styles.chartImg}
        />
      )}

      <DataTable rows={msg.table_data} />
      <SqlBlock sql={msg.sql_generated} />

      {msg.follow_up_suggestions?.length > 0 && (
        <div>
          <div style={styles.followUpLabel}>Suggested follow-ups</div>
          <div style={styles.followUps}>
            {msg.follow_up_suggestions.map((s, i) => (
              <button key={i} style={styles.followUpBtn} onClick={() => onFollowUp(s)}>
                {s}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendQuestion = async (question) => {
    if (!question.trim() || loading) return
    setMessages(prev => [...prev, { type: 'user', text: question }])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, question }),
      })
      const data = await res.json()

      if (!res.ok) {
        const msg = data.detail?.message || data.detail || 'Something went wrong.'
        setMessages(prev => [...prev, { type: 'error', text: msg }])
      } else {
        if (!sessionId) setSessionId(data.session_id)
        setMessages(prev => [...prev, { type: 'assistant', ...data }])
      }
    } catch {
      setMessages(prev => [...prev, {
        type: 'error',
        text: 'Could not reach the server. Is the backend running on port 8000?',
      }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendQuestion(input)
    }
  }

  const clearChat = async () => {
    if (sessionId) {
      await fetch(`${API_BASE}/sessions/${sessionId}`, { method: 'DELETE' }).catch(() => {})
    }
    setMessages([])
    setSessionId(null)
    setInput('')
  }

  return (
    <div style={styles.app}>
      {/* Header */}
      <div style={styles.header}>
        <span style={{ fontSize: 22 }}>📊</span>
        <div>
          <div style={styles.headerTitle}>Loans BI Assistant</div>
          <div style={styles.headerSub}>Ask anything about your loan portfolio</div>
        </div>
        {sessionId && <div style={styles.sessionBadge}>{sessionId}</div>}
      </div>

      {/* Chat */}
      <div style={styles.chatArea}>
        {messages.length === 0 && !loading ? (
          <div style={styles.emptyState}>
            <div style={styles.emptyIcon}>💬</div>
            <div style={styles.emptyTitle}>Ask a portfolio question</div>
            <div style={styles.emptyDesc}>
              Plain English questions — charts and tables generated automatically.
            </div>
            <div style={styles.sampleGrid}>
              {SAMPLE_QUESTIONS.map((q, i) => (
                <button key={i} style={styles.sampleBtn} onClick={() => sendQuestion(q)}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, i) => {
            if (msg.type === 'user')
              return <div key={i} style={styles.userBubble}>{msg.text}</div>
            if (msg.type === 'error')
              return <div key={i} style={styles.errorCard}>⚠️ {msg.text}</div>
            return (
              <AssistantMessage key={i} msg={msg} onFollowUp={sendQuestion} />
            )
          })
        )}

        {loading && (
          <div style={styles.loadingBubble}>⏳ Generating SQL and chart...</div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={styles.inputArea}>
        {messages.length > 0 && (
          <button style={styles.clearBtn} onClick={clearChat}>Clear</button>
        )}
        <textarea
          ref={inputRef}
          style={styles.textarea}
          value={input}
          placeholder="Ask a question about your loan portfolio…"
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
        />
        <button
          style={{ ...styles.sendBtn, ...(loading || !input.trim() ? styles.sendBtnDisabled : {}) }}
          onClick={() => sendQuestion(input)}
          disabled={loading || !input.trim()}
        >
          {loading ? '...' : 'Ask →'}
        </button>
      </div>
    </div>
  )
}