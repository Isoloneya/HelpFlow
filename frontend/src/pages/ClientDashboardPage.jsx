import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client.js'

const statusLabels = {
  new: 'Нове',
  in_progress: 'В роботі',
  resolved: 'Вирішено',
  closed: 'Закрито',
}

const priorityClasses = {
  low: 'bg-sunken text-muted',
  medium: 'bg-sunken text-ink',
  high: 'bg-[#FFF1D7] text-risk',
  urgent: 'bg-[#FCE3DF] text-breach',
}

const priorityLabels = { low: 'Низький', medium: 'Середній', high: 'Високий', urgent: 'Терміновий' }

function ClientDashboardPage() {
  const [tickets, setTickets] = useState([])
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .get('/tickets')
      .then(setTickets)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const filteredTickets = status ? tickets.filter((ticket) => ticket.status === status) : tickets

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold">Мої звернення</h1>
          <p className="mt-1 text-sm text-muted">Статус, пріоритет і листування з командою підтримки.</p>
        </div>
        <Link to="/my-tickets/new" className="rounded-lg bg-accent px-4 py-2.5 text-xs font-semibold text-white">
          Створити звернення
        </Link>
      </div>
      <div className="mt-6 flex flex-wrap gap-2">{[['', 'Усі'], ...Object.entries(statusLabels)].map(([value, label]) => <button key={value || 'all'} type="button" onClick={() => setStatus(value)} className={`rounded-lg px-4 py-2 text-xs font-semibold transition-colors ${status === value ? 'bg-accent text-white' : 'bg-surface text-muted hover:text-ink'}`}>{label}<span className="ml-2 rounded-full bg-white/20 px-1.5 py-0.5 text-[10px]">{value ? tickets.filter((ticket) => ticket.status === value).length : tickets.length}</span></button>)}</div>
      {loading && <p className="mt-8 text-sm text-muted">Завантаження...</p>}
      {error && <p role="alert" className="mt-6 rounded-lg bg-[#FCE3DF] p-3 text-sm text-breach">{error}</p>}
      {!loading && !error && filteredTickets.length === 0 && (
        <div className="mt-7 rounded-xl border border-dashed border-line bg-surface p-8 text-center">
          <p className="text-sm text-muted">У вас поки немає звернень.</p>
        </div>
      )}
      {filteredTickets.length > 0 && <div className="mt-6 overflow-hidden rounded-xl border border-line bg-surface"><div className="hidden grid-cols-[64px_minmax(220px,1fr)_160px_130px_130px_130px_130px] gap-4 border-b border-line bg-sunken px-5 py-3 text-[11px] font-semibold uppercase tracking-wide text-muted lg:grid"><span>#</span><span>Тема</span><span>Категорія</span><span>Статус</span><span>Пріоритет</span><span>SLA</span><span>Створено</span></div>{filteredTickets.map((ticket) => <Link key={ticket.id} to={`/my-tickets/${ticket.id}`} className="grid gap-2 border-b border-line px-5 py-4 transition-colors last:border-0 hover:bg-sunken lg:grid-cols-[64px_minmax(220px,1fr)_160px_130px_130px_130px_130px] lg:items-center lg:gap-4"><span className="font-mono text-xs text-muted">#{ticket.id}</span><div><p className="font-semibold">{ticket.title}</p><p className="mt-1 text-xs text-muted lg:hidden">Створено {new Date(ticket.created_at).toLocaleString('uk-UA')}</p></div><span className="text-xs text-muted">{ticket.category_name}</span><span className="w-fit rounded-full bg-[#E7F2EB] px-2.5 py-1 text-[11px] font-semibold text-ok">{statusLabels[ticket.status]}</span><span className={`w-fit rounded-full px-2.5 py-1 text-[11px] font-semibold ${priorityClasses[ticket.priority]}`}>{priorityLabels[ticket.priority]}</span><span className={ticket.sla_breached ? 'text-xs font-semibold text-breach' : 'text-xs text-muted'}>{new Date(ticket.sla_deadline).toLocaleDateString('uk-UA')}</span><span className="hidden text-xs text-muted lg:block">{new Date(ticket.created_at).toLocaleDateString('uk-UA')}</span></Link>)}</div>}
    </div>
  )
}

export default ClientDashboardPage
