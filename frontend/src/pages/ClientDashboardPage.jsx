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

function ClientDashboardPage() {
  const [tickets, setTickets] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .get('/tickets')
      .then(setTickets)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-3xl">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold">Мої звернення</h1>
          <p className="mt-1 text-sm text-muted">Статус і листування з командою підтримки.</p>
        </div>
        <Link to="/my-tickets/new" className="rounded-lg bg-accent px-4 py-2.5 text-xs font-semibold text-white">
          Створити звернення
        </Link>
      </div>
      {loading && <p className="mt-8 text-sm text-muted">Завантаження...</p>}
      {error && <p role="alert" className="mt-6 rounded-lg bg-[#FCE3DF] p-3 text-sm text-breach">{error}</p>}
      {!loading && !error && tickets.length === 0 && (
        <div className="mt-7 rounded-xl border border-dashed border-line bg-surface p-8 text-center">
          <p className="text-sm text-muted">У вас поки немає звернень.</p>
        </div>
      )}
      <div className="mt-6 grid gap-3">
        {tickets.map((ticket) => (
          <Link key={ticket.id} to={`/my-tickets/${ticket.id}`} className="rounded-xl border border-line bg-surface p-4 transition-colors hover:border-accent">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="font-display text-base font-semibold">{ticket.title}</p>
                <p className="mt-1 text-xs text-muted">#{ticket.id} · до {new Date(ticket.sla_deadline).toLocaleString('uk-UA')}</p>
              </div>
              <div className="flex gap-2">
                <span className={`rounded-full px-2.5 py-1 text-[11px] font-semibold ${priorityClasses[ticket.priority]}`}>{ticket.priority}</span>
                <span className="rounded-full bg-sunken px-2.5 py-1 text-[11px] font-semibold text-ink">{statusLabels[ticket.status]}</span>
              </div>
            </div>
            {ticket.sla_breached && <p className="mt-3 text-xs font-semibold text-breach">Термін SLA порушено</p>}
          </Link>
        ))}
      </div>
    </div>
  )
}

export default ClientDashboardPage
