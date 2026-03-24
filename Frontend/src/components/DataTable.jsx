export default function DataTable({ rows }) {
  if (!rows || rows.length === 0) return null
  const cols = Object.keys(rows[0])
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>{cols.map(c => <th key={c} className="th">{c}</th>)}</tr>
        </thead>
        <tbody>
          {rows.slice(0, 20).map((row, i) => (
            <tr key={i} style={{ background: i % 2 === 0 ? '#fff' : '#fafafa' }}>
              {cols.map(c => (
                <td key={c} className="td">
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
