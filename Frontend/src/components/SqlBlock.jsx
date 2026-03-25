import { useState } from 'react'

export default function SqlBlock({ sql }) {
  const [show, setShow] = useState(true)
  return (
    <div>
      <button className="sql-toggle" onClick={() => setShow(v => !v)}>
        {show ? '▾ Hide SQL' : '▸ View generated SQL'}
      </button>
      {show && <pre className="sql-block">{sql}</pre>}
    </div>
  )
}
