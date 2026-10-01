import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client.js'

const columns = [
  ['new', 'Нові'],
  ['in_progress', 'В роботі'],
  ['resolved', 'Вирішені'],
  ['closed', 'Закриті'],
]

const priorityClasses = {
  low: 'bg-sunken text-muted',
  medium: 'bg-sunken text-ink',
  high: 'bg-[#FFF1D7] text-risk',
  urgent: 'bg-[#FCE3DF] text-breach',
}

function OperatorBoardPage() {
  const [tickets, setTickets] = useState([])
  const [categories, setCategories] = useState([])
  const [priority, setPriority] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/categories').then(setCategories).catch((err) => setError(err.message))
  }, [])

  useEffect(() => {
    const params = new URLSearchParams()
    if (priority) params.set('priority', priority)
    if (categoryId) params.set('category_id', categoryId)
    const query = params.toString()
    setLoading(true)
    api
      .get(`/tickets${query ? `?${query}` : ''}`)
      .then(setTickets)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [priority, categoryId])

  return (
    <div>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold">Дошка звернень</h1>
          <p className="mt-1 text-sm text-muted">Призначені звернення та їхній поточний стан.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <select value={priority} onChange={(event) => setPriority(event.target.value)} className="rounded-lg border border-line bg-surface px-3 py-2 text-xs">
            <option value="">Усі пріоритети</option>
            <option value="low">Низький</option>
            <option value="medium">Середній</option>
            <option value="high">Високий</option>
            <option value="urgent">Терміновий</option>
          </select>
          <select value={categoryId} onChange={(event) => setCategoryId(event.target.value)} className="rounded-lg border border-line bg-surface px-3 py-2 text-xs">
            <option value="">Усі категорії</option>
            {categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
          </select>
        </div>
      </div>
      {error && <p role="alert" className="mt-5 rounded-lg bg-[#FCE3DF] p-3 text-sm text-breach">{error}</p>}
      {loading ? <p className="mt-8 text-sm text-muted">Завантаження...</p> : <div className="mt-6 grid gap-4 overflow-x-auto pb-3 md:grid-cols-2 xl:grid-cols-4">{columns.map(([status, label]) => {
        const columnTickets = tickets.filter((ticket) => ticket.status === status)
        return <section key={status} className="min-w-[250px] rounded-xl bg-sunken p-3"><div className="flex items-center justify-between px-1"><h2 className="font-display text-sm font-semibold">{label}</h2><span className="rounded-full bg-surface px-2 py-0.5 text-[11px] font-semibold text-muted">{columnTickets.length}</span></div><div className="mt-3 grid gap-3">{columnTickets.map((ticket) => <Link key={ticket.id} to={`/tickets/${ticket.id}`} className="rounded-lg border border-line bg-surface p-4 shadow-sm transition-colors hover:border-accent"><div className="flex items-start justify-between gap-2"><p className="text-sm font-semibold leading-snug">{ticket.title}</p><span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold ${priorityClasses[ticket.priority]}`}>{ticket.priority}</span></div><p className="mt-3 text-[11px] text-muted">#{ticket.id} · до {new Date(ticket.sla_deadline).toLocaleString('uk-UA')}</p>{ticket.sla_breached && <p className="mt-2 text-[11px] font-semibold text-breach">SLA порушено</p>}</Link>)}{columnTickets.length === 0 && <p className="rounded-lg border border-dashed border-line p-3 text-center text-xs text-muted">Немає звернень</p>}</div></section>
      })}</div>}
    </div>
  )
}

export default OperatorBoardPage
