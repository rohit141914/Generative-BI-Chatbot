import { useState, useRef, useEffect } from 'react'
import './App.css'
import { SAMPLE_QUESTIONS } from './constants'
import AssistantMessage from './components/AssistantMessage'
import { postChat, deleteSession, getSession } from './api'

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    const savedSession = localStorage.getItem('bi_session_id')
    if (!savedSession) return

    getSession(savedSession)
      .then(data => {
        setSessionId(savedSession)
        const restored = data.history.flatMap(turn => [
          { type: 'user', text: turn.question },
          { type: 'assistant', ...turn.response },
        ])
        setMessages(restored)
      })
      .catch(() => {
        localStorage.removeItem('bi_session_id')
      })
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendQuestion = async (question) => {
    if (!question.trim() || loading) return
    setMessages(prev => [...prev, { type: 'user', text: question }])
    setInput('')
    setLoading(true)

    try {
      const data = await postChat(sessionId, question)
      if (!sessionId) {
        setSessionId(data.session_id)
        localStorage.setItem('bi_session_id', data.session_id)
      }
      setMessages(prev => [...prev, { type: 'assistant', ...data }])
    } catch (err) {
      const msg = err.response?.data?.detail?.message
        || err.response?.data?.detail
        || 'Could not reach the server. Is the backend running on port 8000?'
      setMessages(prev => [...prev, { type: 'error', text: msg }])
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
      await deleteSession(sessionId)
    }
    setMessages([])
    setSessionId(null)
    localStorage.removeItem('bi_session_id')
    setInput('')
  }

  return (
    <div className="app">
      {/* Header */}
      <div className="header">
        <span style={{ fontSize: 22 }}>📊</span>
        <div>
          <div className="header-title">Loans BI Assistant</div>
          <div className="header-sub">Ask anything about your loan portfolio</div>
        </div>
        {sessionId && <div className="session-badge">{sessionId}</div>}
      </div>

      {/* Chat */}
      <div className="chat-area">
        {messages.length === 0 && !loading ? (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <div className="empty-title">Ask a portfolio question</div>
            <div className="empty-desc">
              Plain English questions — charts and tables generated automatically.
            </div>
            <div className="sample-grid">
              {SAMPLE_QUESTIONS.map((q, i) => (
                <button key={i} className="sample-btn" onClick={() => sendQuestion(q)}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, i) => {
            if (msg.type === 'user')
              return <div key={i} className="user-bubble">{msg.text}</div>
            if (msg.type === 'error')
              return <div key={i} className="error-card">⚠️ {msg.text}</div>
            return (
              <AssistantMessage key={i} msg={msg} onFollowUp={sendQuestion} />
            )
          })
        )}

        {loading && (
          <div className="loading-bubble">⏳ Generating SQL and chart...</div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="input-area">
        {messages.length > 0 && (
          <button className="clear-btn" onClick={clearChat}>Clear</button>
        )}
        <textarea
          ref={inputRef}
          className="textarea"
          value={input}
          placeholder="Ask a question about your loan portfolio…"
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
        />
        <button
          className={`send-btn${loading || !input.trim() ? ' send-btn-disabled' : ''}`}
          onClick={() => sendQuestion(input)}
          disabled={loading || !input.trim()}
        >
          {loading ? '...' : 'Ask →'}
        </button>
      </div>
    </div>
  )
}
