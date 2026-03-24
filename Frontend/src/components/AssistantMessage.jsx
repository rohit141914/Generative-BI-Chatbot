import { API_BASE } from '../constants'
import DataTable from './DataTable'
import SqlBlock from './SqlBlock'

export default function AssistantMessage({ msg, onFollowUp }) {
  return (
    <div className="assistant-card">
      <p className="answer-text">{msg.answer_text}</p>

      {msg.chart_url && (
        <img
          src={`${API_BASE}${msg.chart_url}`}
          alt="chart"
          className="chart-img"
        />
      )}

      <DataTable rows={msg.table_data} />
      <SqlBlock sql={msg.sql_generated} />

      {msg.follow_up_suggestions?.length > 0 && (
        <div>
          <div className="follow-up-label">Suggested follow-ups</div>
          <div className="follow-ups">
            {msg.follow_up_suggestions.map((s, i) => (
              <button key={i} className="follow-up-btn" onClick={() => onFollowUp(s)}>
                {s}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
