import { useEffect, useState } from 'react'
import { api } from '../api/client.js'

function AgentsPage() {
  const [agents, setAgents] = useState([])
  const [email, setEmail] = useState('')
  const [temporaryPassword, setTemporaryPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function loadAgents() {
    try {
      const data = await api.get('/users')
      setAgents(data)
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    loadAgents()
  }, [])

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setTemporaryPassword('')
    setSubmitting(true)

    try {
      const agent = await api.post('/users', { email: email.trim() })
      setAgents((current) => [...current, agent])
      setTemporaryPassword(agent.temporary_password)
      setEmail('')
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold">Агенти</h1>
      <p className="mt-1 text-sm text-muted">Керування командою підтримки та її правами доступу.</p>

      <form
        onSubmit={handleSubmit}
        className="mt-6 flex flex-wrap gap-3 rounded-xl border border-line bg-surface p-5"
      >
        <input
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="email агента"
          type="email"
          required
          className="min-w-[220px] flex-1 rounded-lg border border-line px-3 py-2.5 text-sm focus:border-accent focus:outline-none"
        />
        <button
          type="submit"
          disabled={submitting}
          className="rounded-lg bg-accent px-5 py-2.5 text-xs font-semibold text-white disabled:opacity-60"
        >
          {submitting ? 'Створення...' : 'Створити агента'}
        </button>
      </form>

      {temporaryPassword && (
        <div className="mt-4 rounded-xl bg-[#FFF1D7] p-4">
          <p className="text-xs font-semibold text-risk">Тимчасовий пароль</p>
          <p className="mt-2 break-all font-mono text-sm">{temporaryPassword}</p>
        </div>
      )}

      {error && (
        <p role="alert" className="mt-4 rounded-lg bg-[#FCE3DF] p-3 text-sm text-breach">
          {error}
        </p>
      )}

      <div className="mt-6 overflow-hidden rounded-xl border border-line bg-surface">
        <div className="hidden grid-cols-[1fr_150px] gap-4 border-b border-line bg-sunken px-5 py-3 text-[11px] font-semibold uppercase tracking-wide text-muted sm:grid"><span>Email</span><span>Роль</span></div>
        {agents.map((agent) => (
          <article
            key={agent.id}
            className="flex flex-wrap items-center justify-between gap-2 border-b border-line p-4 last:border-0 sm:grid sm:grid-cols-[1fr_150px] sm:gap-4 sm:px-5"
          >
            <p className="font-semibold">{agent.email}</p>
            <span className="rounded-full bg-sunken px-2.5 py-1 text-xs font-semibold text-muted">
              {agent.role}
            </span>
          </article>
        ))}
      </div>
    </div>
  )
}

export default AgentsPage
