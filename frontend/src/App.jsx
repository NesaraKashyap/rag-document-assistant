import { useState } from 'react'
import './App.css'

function App() {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const askQuestion = async () => {
    if (question.trim() === '') return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('http://127.0.0.1:8000/v1/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question })
      })

      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <h1>NimbusDesk RAG Assistant</h1>
      <p>Ask a question about NimbusDesk's policies, and get a grounded answer with sources.</p>

      <div className="input-row">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question..."
        />
        <button onClick={askQuestion} disabled={loading}>
          {loading ? 'Thinking...' : 'Ask'}
        </button>
      </div>

      {error && <p className="error">Error: {error}</p>}

      {result && (
        <div className="result">
          <h2>Answer</h2>
          <p>{result.answer}</p>

          <h2>Sources</h2>
          <ul>
            {result.sources.map((source) => (
              <li key={source.citation_number}>
                [{source.citation_number}] {source.source_file} &gt; {source.heading}
              </li>
            ))}
          </ul>

          <h2>Citation Verification</h2>
          <ul>
            {result.verification.map((v, index) => (
              <li key={index} className={`verdict-${v.verdict.toLowerCase()}`}>
                [{v.verdict}] {v.sentence}
              </li>
            ))}
          </ul>

          <p className="timing">
            Retrieval: {result.retrieval_time_seconds}s | Generation: {result.generation_time_seconds}s
          </p>
        </div>
      )}
    </div>
  )
}

export default App