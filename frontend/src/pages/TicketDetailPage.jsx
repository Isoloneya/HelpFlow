import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'

const statusLabels = { new: 'Нове', in_progress: 'В роботі', resolved: 'Вирішено', closed: 'Закрито' }
const priorityLabels = { low: 'Низький', medium: 'Середній', high: 'Високий', urgent: 'Терміновий' }

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

  async function changePriority(priority) {
    setError('')
    try {
      const updated = await api.patch(`/tickets/${id}`, { priority })
      setTicket(updated)
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <p className="text-sm text-muted">Завантаження...</p>
  if (error && !ticket) return <div><Link to={backPath} className="text-xs font-semibold text-accent">← Назад</Link><p role="alert" className="mt-5 text-sm text-breach">{error}</p></div>

  return (
    <div className="mx-auto max-w-5xl">
      <Link to={backPath} className="text-xs font-semibold text-accent">← Назад до списку</Link>
      <section className="mt-4 rounded-xl border border-line bg-surface p-5 shadow-sm sm:p-7">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div><p className="text-xs font-semibold text-muted">Звернення #{ticket.id}</p><h1 className="mt-1 text-2xl font-semibold">{ticket.title}</h1></div>
          <span className="rounded-full bg-sunken px-2.5 py-1 text-xs font-semibold">{statusLabels[ticket.status]}</span>
        </div>
        <p className="mt-5 whitespace-pre-wrap text-sm leading-relaxed text-ink">{ticket.description}</p>
        <div className="mt-6 grid gap-3 border-t border-line pt-5 text-xs text-muted sm:grid-cols-3">
          <div><p className="font-semibold uppercase tracking-wide">Пріоритет</p><p className="mt-1 text-sm text-ink">{priorityLabels[ticket.priority]}</p></div><div><p className="font-semibold uppercase tracking-wide">SLA</p><p className="mt-1 text-sm text-ink">{new Date(ticket.sla_deadline).toLocaleString('uk-UA')}</p></div><div><p className="font-semibold uppercase tracking-wide">Створено</p><p className="mt-1 text-sm text-ink">{new Date(ticket.created_at).toLocaleString('uk-UA')}</p></div>
        </div>
        {ticket.sla_breached && <p className="mt-4 text-xs font-semibold text-breach">Термін SLA порушено</p>}
        {isStaff && <div className="mt-5 grid gap-4 border-t border-line pt-5 sm:grid-cols-2"><div><p className="mb-2 text-xs font-semibold text-muted">Статус</p><div className="flex flex-wrap gap-2">{Object.entries(statusLabels).map(([value, label]) => <button key={value} onClick={() => changeStatus(value)} disabled={value === ticket.status} className="rounded-lg border border-line px-3 py-2 text-xs font-semibold disabled:bg-sunken disabled:text-muted">{label}</button>)}</div></div><div><label className="mb-2 block text-xs font-semibold text-muted">Пріоритет</label><select value={ticket.priority} onChange={(event) => changePriority(event.target.value)} className="w-full rounded-lg border border-line bg-surface px-3 py-2 text-sm focus:border-accent focus:outline-none">{Object.entries(priorityLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div></div>}
      </section>
      <section className="mt-5 overflow-hidden rounded-xl border border-line bg-surface shadow-sm">
        <div className="border-b border-line px-5 py-4 sm:px-7"><h2 className="text-lg font-semibold">Переписка</h2><p className="mt-1 text-xs text-muted">Повідомлення за зверненням</p></div>
        <div className="px-5 py-5 sm:px-7">{comments.length === 0 && <p className="py-6 text-center text-sm text-muted">Повідомлень поки немає.</p>}<div className="relative grid gap-5 border-l border-line pl-5">{comments.map((comment) => <article key={comment.id} className="relative"><span className={`absolute -left-[25px] top-1 h-2.5 w-2.5 rounded-full ring-4 ring-surface ${comment.is_internal ? 'bg-risk' : 'bg-accent'}`} /><div className="flex flex-wrap items-center justify-between gap-2 text-[11px] font-semibold text-muted"><span>{comment.is_internal ? 'Внутрішня нотатка' : comment.author_id === user.id ? 'Ви' : 'Команда підтримки'}</span><time>{new Date(comment.created_at).toLocaleString('uk-UA')}</time></div><div className={`mt-2 max-w-3xl rounded-lg px-4 py-3 text-sm leading-relaxed ${comment.is_internal ? 'bg-[#FFF1D7]' : comment.author_id === user.id ? 'bg-[#E7F2EB]' : 'bg-sunken'}`}><p className="whitespace-pre-wrap">{comment.body}</p></div></article>)}</div></div>
        <form onSubmit={addComment} className="border-t border-line bg-sunken p-5 sm:px-7"><label className="mb-2 block text-xs font-semibold text-muted">Нове повідомлення</label><div className="flex items-end gap-3"><textarea value={body} onChange={(event) => setBody(event.target.value)} minLength="1" maxLength="2000" required rows="3" placeholder="Написати відповідь..." className="min-h-[76px] flex-1 resize-none rounded-lg border border-line bg-surface px-3 py-2.5 text-sm focus:border-accent focus:outline-none" /><button type="submit" className="rounded-lg bg-accent px-5 py-3 text-xs font-semibold text-white">Надіслати</button></div>{isStaff && <label className="mt-3 flex items-center gap-2 text-xs text-muted"><input type="checkbox" checked={isInternal} onChange={(event) => setIsInternal(event.target.checked)} />Внутрішня нотатка</label>}{error && <p role="alert" className="mt-3 text-sm text-breach">{error}</p>}</form>
      </section>
    </div>
  )
}

export default TicketDetailPage
