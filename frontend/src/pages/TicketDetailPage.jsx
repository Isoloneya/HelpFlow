import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'

const statusLabels = { new: 'Нове', in_progress: 'В роботі', resolved: 'Вирішено', closed: 'Закрито' }

function TicketDetailPage() {
  const { id } = useParams()
  const { user } = useAuth()
  const [ticket, setTicket] = useState(null)
  const [comments, setComments] = useState([])
  const [body, setBody] = useState('')
  const [isInternal, setIsInternal] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const isStaff = user.role !== 'client'
  const backPath = isStaff ? '/dashboard' : '/my-tickets'

  async function loadTicket() {
    setLoading(true)
    setError('')
    try {
      const [ticketData, commentData] = await Promise.all([api.get(`/tickets/${id}`), api.get(`/tickets/${id}/comments`)])
      setTicket(ticketData)
      setComments(commentData)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadTicket() }, [id])

  async function addComment(event) {
    event.preventDefault()
    setError('')
    try {
      const comment = await api.post(`/tickets/${id}/comments`, { body: body.trim(), is_internal: isInternal })
      setComments((current) => [...current, comment])
      setBody('')
      setIsInternal(false)
    } catch (err) {
      setError(err.message)
    }
  }

  async function changeStatus(status) {
    setError('')
    try {
      const updated = await api.patch(`/tickets/${id}`, { status })
      setTicket(updated)
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <p className="text-sm text-muted">Завантаження...</p>
  if (error && !ticket) return <div><Link to={backPath} className="text-xs font-semibold text-accent">← Назад</Link><p role="alert" className="mt-5 text-sm text-breach">{error}</p></div>

  return (
    <div className="mx-auto max-w-3xl">
      <Link to={backPath} className="text-xs font-semibold text-accent">← Назад</Link>
      <section className="mt-4 rounded-xl border border-line bg-surface p-5 sm:p-7">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div><p className="text-xs font-semibold text-muted">Звернення #{ticket.id}</p><h1 className="mt-1 text-xl font-semibold">{ticket.title}</h1></div>
          <span className="rounded-full bg-sunken px-2.5 py-1 text-xs font-semibold">{statusLabels[ticket.status]}</span>
        </div>
        <p className="mt-5 whitespace-pre-wrap text-sm leading-relaxed text-ink">{ticket.description}</p>
        <div className="mt-5 flex flex-wrap gap-x-5 gap-y-2 text-xs text-muted">
          <span>Пріоритет: {ticket.priority}</span><span>SLA: {new Date(ticket.sla_deadline).toLocaleString('uk-UA')}</span>
        </div>
        {ticket.sla_breached && <p className="mt-4 text-xs font-semibold text-breach">Термін SLA порушено</p>}
        {isStaff && <div className="mt-5 flex flex-wrap gap-2">{Object.entries(statusLabels).map(([value, label]) => <button key={value} onClick={() => changeStatus(value)} disabled={value === ticket.status} className="rounded-lg border border-line px-3 py-2 text-xs font-semibold disabled:bg-sunken disabled:text-muted">{label}</button>)}</div>}
      </section>
      <section className="mt-5 rounded-xl border border-line bg-surface p-5 sm:p-7">
        <h2 className="text-lg font-semibold">Листування</h2>
        <div className="mt-5 grid gap-3">{comments.length === 0 && <p className="text-sm text-muted">Повідомлень поки немає.</p>}{comments.map((comment) => <article key={comment.id} className={`rounded-lg p-3.5 ${comment.is_internal ? 'bg-[#FFF1D7]' : 'bg-sunken'}`}><div className="flex justify-between gap-3 text-[11px] font-semibold text-muted"><span>{comment.is_internal ? 'Внутрішня нотатка' : 'Повідомлення'}</span><time>{new Date(comment.created_at).toLocaleString('uk-UA')}</time></div><p className="mt-2 whitespace-pre-wrap text-sm">{comment.body}</p></article>)}</div>
        <form onSubmit={addComment} className="mt-6"><label className="mb-1.5 block text-xs font-semibold text-muted">Нове повідомлення</label><textarea value={body} onChange={(event) => setBody(event.target.value)} minLength="1" maxLength="2000" required rows="4" className="w-full rounded-lg border border-line px-3 py-2.5 text-sm focus:border-accent focus:outline-none" />{isStaff && <label className="mt-3 flex items-center gap-2 text-xs text-muted"><input type="checkbox" checked={isInternal} onChange={(event) => setIsInternal(event.target.checked)} />Внутрішня нотатка</label>}{error && <p role="alert" className="mt-3 text-sm text-breach">{error}</p>}<button type="submit" className="mt-4 rounded-lg bg-accent px-5 py-2.5 text-xs font-semibold text-white">Надіслати</button></form>
      </section>
    </div>
  )
}

export default TicketDetailPage
