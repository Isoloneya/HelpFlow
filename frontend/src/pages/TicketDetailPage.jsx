import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'
import { useToast } from '../context/ToastContext.jsx'

const statusLabels = { new: 'Нове', in_progress: 'В роботі', resolved: 'Вирішено', closed: 'Закрито' }
const priorityLabels = { low: 'Низький', medium: 'Середній', high: 'Високий', urgent: 'Терміновий' }

function formatDate(value) {
  return new Date(value).toLocaleString('uk-UA', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function TicketDetailPage() {
  const { id } = useParams()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [ticket, setTicket] = useState(null)
  const [comments, setComments] = useState([])
  const [agents, setAgents] = useState([])
  const [categories, setCategories] = useState([])
  const [imageUrls, setImageUrls] = useState({})
  const [body, setBody] = useState('')
  const [files, setFiles] = useState([])
  const [isInternal, setIsInternal] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const isStaff = user.role !== 'client'
  const backPath = isStaff ? '/dashboard' : '/my-tickets'

  async function loadTicket() {
    setLoading(true)
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
  useEffect(() => { if (isStaff) api.get('/users').then(setAgents).catch((err) => setError(err.message)) }, [isStaff])
  useEffect(() => { if (isStaff) api.get('/categories').then(setCategories).catch((err) => setError(err.message)) }, [isStaff])
  useEffect(() => {
    if (!ticket) return undefined
    let active = true
    const urls = []
    const attachments = [...ticket.attachments, ...comments.flatMap((comment) => comment.attachments || [])].filter((attachment) => attachment.content_type.startsWith('image/'))
    Promise.all(attachments.map(async (attachment) => {
      const url = URL.createObjectURL(await api.download(`/tickets/${ticket.id}/attachments/${attachment.id}`))
      urls.push(url)
      return [attachment.id, url]
    })).then((entries) => { if (active) setImageUrls(Object.fromEntries(entries)) }).catch((err) => setError(err.message))
    return () => { active = false; urls.forEach((url) => URL.revokeObjectURL(url)) }
  }, [ticket?.id, comments])

  async function updateTicket(data, message) {
    try {
      const updated = await api.patch(`/tickets/${id}`, data)
      setTicket(updated)
      showToast(message)
    } catch (err) {
      setError(err.message)
    }
  }

  async function addComment(event) {
    event.preventDefault()
    try {
      let comment
      if (files.length) {
        const formData = new FormData()
        formData.append('body', body.trim())
        formData.append('is_internal', String(isInternal))
        files.forEach((file) => formData.append('files', file))
        comment = await api.postForm(`/tickets/${id}/comments`, formData)
      } else {
        comment = await api.post(`/tickets/${id}/comments`, { body: body.trim(), is_internal: isInternal })
      }
      setComments((current) => [...current, comment])
      setBody('')
      setFiles([])
      setIsInternal(false)
      showToast('Повідомлення надіслано')
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <p className="text-sm text-muted">Завантаження...</p>
  if (!ticket) return <p role="alert" className="text-sm text-breach">{error}</p>

  const timeline = [{ id: 'description', body: ticket.description, author_id: ticket.client_id, created_at: ticket.created_at, attachments: [] }, ...comments]
  const locked = ticket.status === 'resolved' || ticket.status === 'closed'

  return <div className="mx-auto max-w-[1180px]">
    <Link to={backPath} className="text-xs font-semibold text-accent">← Назад до списку</Link>
    <div className="mt-3 flex flex-wrap items-start justify-between gap-3"><div><h1 className="text-2xl font-semibold">{ticket.title}</h1><p className="mt-1 text-xs text-muted">#{ticket.id} · Створено {formatDate(ticket.created_at)}</p></div><div className="flex gap-2"><span className="rounded-full bg-[#FCE3DF] px-2.5 py-1 text-xs font-semibold text-breach">{ticket.priority}</span><span className="rounded-full bg-[#E6F0FF] px-2.5 py-1 text-xs font-semibold text-[#2364B7]">{statusLabels[ticket.status]}</span></div></div>
    {isStaff && <section className="mt-4 flex flex-wrap items-center gap-3 rounded-xl border border-line bg-surface px-4 py-3"><span className="text-xs font-semibold text-muted">Оператори в зверненні:</span>{ticket.participants.map((operator) => <span key={operator.id} className="rounded-full bg-[#E7F2EB] px-2.5 py-1 text-xs font-semibold text-ok">{operator.full_name}</span>)}<select value="" onChange={(event) => { const operatorId = Number(event.target.value); if (operatorId && !ticket.participant_ids.includes(operatorId)) updateTicket({ participant_ids: [...ticket.participant_ids, operatorId] }, 'Оператора додано до звернення') }} className="rounded-lg border border-line bg-surface px-3 py-1.5 text-xs"><option value="">Додати оператора</option>{agents.filter((agent) => agent.role === 'agent' && agent.is_active && !ticket.participant_ids.includes(agent.id)).map((agent) => <option key={agent.id} value={agent.id}>{agent.full_name}</option>)}</select></section>}
    <div className="mt-4 grid gap-5 lg:grid-cols-[minmax(0,1fr)_300px]">
      <section className="self-start overflow-hidden rounded-xl border border-line bg-surface shadow-sm"><div className="border-b border-line px-5 py-4"><h2 className="text-lg font-semibold">Переписка</h2><p className="mt-1 text-xs text-muted">Повідомлення за зверненням</p></div><div className="px-5 py-5"><div className="grid gap-5 border-l border-line pl-5">{timeline.map((item) => { const clientMessage = item.author_id === ticket.client_id; return <article key={item.id} className="relative"><span className="absolute -left-[25px] top-1 h-2.5 w-2.5 rounded-full bg-accent ring-4 ring-surface" /><div className="flex justify-between gap-2 text-[11px] font-semibold text-muted"><span>{item.is_internal ? 'Внутрішня нотатка' : clientMessage ? 'Клієнт' : item.author_id === user.id ? 'Ви' : 'Агент підтримки'}</span><time>{formatDate(item.created_at)}</time></div>{item.body && <p className={`mt-2 whitespace-pre-wrap rounded-lg px-4 py-3 text-sm ${clientMessage ? 'bg-sunken' : 'bg-[#E7F2EB]'}`}>{item.body}</p>}{item.attachments?.length > 0 && <div className="mt-2 flex flex-wrap gap-2">{item.attachments.map((attachment) => imageUrls[attachment.id] ? <a key={attachment.id} href={imageUrls[attachment.id]} target="_blank" rel="noreferrer"><img src={imageUrls[attachment.id]} alt={attachment.filename} className="h-20 w-20 rounded-md border border-line object-cover" /></a> : <span key={attachment.id} className="rounded bg-sunken px-2 py-1 text-xs">{attachment.filename}</span>)}</div>}</article> })}</div></div>{locked ? <div className="border-t border-line bg-sunken p-4 text-center text-xs font-semibold text-muted">Листування закрито. {!isStaff && <Link to={`/my-tickets/new?follow_up_of=${ticket.id}`} className="text-accent">Створити повторне звернення</Link>}</div> : <form onSubmit={addComment} className="border-t border-line bg-sunken p-4"><div className="flex items-end gap-2"><textarea value={body} onChange={(event) => setBody(event.target.value)} placeholder="Написати відповідь..." rows="2" maxLength="2000" className="min-h-[56px] flex-1 resize-none rounded-lg border border-line bg-surface px-3 py-2 text-sm" /><label className="cursor-pointer rounded-lg border border-line bg-surface px-3 py-3 text-xs font-semibold">Файл<input type="file" multiple className="sr-only" onChange={(event) => setFiles(Array.from(event.target.files || []))} /></label><button type="submit" className="rounded-lg bg-accent px-4 py-3 text-xs font-semibold text-white">Надіслати</button></div>{files.length > 0 && <p className="mt-2 text-xs text-muted">{files.map((file) => file.name).join(', ')}</p>}{isStaff && <label className="mt-3 flex items-center gap-2 text-xs text-muted"><input type="checkbox" checked={isInternal} onChange={(event) => setIsInternal(event.target.checked)} />Внутрішня нотатка</label>}{error && <p className="mt-3 text-sm text-breach">{error}</p>}</form>}</section>
      <aside className="h-fit rounded-xl border border-line bg-surface p-5 shadow-sm"><h2 className="text-base font-semibold">Деталі звернення</h2><dl className="mt-5 grid gap-4 text-sm"><div><dt className="text-xs text-muted">Статус</dt><dd className="mt-1 font-medium">{statusLabels[ticket.status]}</dd></div><div><dt className="text-xs text-muted">Пріоритет</dt><dd className="mt-1 font-medium">{priorityLabels[ticket.priority]}</dd></div><div><dt className="text-xs text-muted">Категорія</dt><dd className="mt-1 font-medium">{ticket.category_name}</dd></div><div><dt className="text-xs text-muted">SLA</dt><dd className="mt-1 font-medium">{formatDate(ticket.sla_deadline)}</dd></div><div><dt className="text-xs text-muted">Автор</dt><dd className="mt-1 font-medium">{ticket.client_name || ticket.client_email}</dd></div><div><dt className="text-xs text-muted">Призначено</dt><dd className="mt-1 font-medium">{ticket.assignee_email || 'Не призначено'}</dd></div></dl>{isStaff && <div className="mt-6 grid gap-3 border-t border-line pt-5"><label className="text-xs font-semibold text-muted">Статус<select value={ticket.status} onChange={(event) => updateTicket({ status: event.target.value }, 'Статус оновлено')} className="mt-1 w-full rounded-lg border border-line bg-surface px-3 py-2 text-sm">{Object.entries(statusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label><label className="text-xs font-semibold text-muted">Категорія<select value={ticket.category_id} onChange={(event) => updateTicket({ category_id: Number(event.target.value) }, 'Категорію оновлено')} className="mt-1 w-full rounded-lg border border-line bg-surface px-3 py-2 text-sm">{categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select></label><label className="text-xs font-semibold text-muted">Виконавець<select value={ticket.assignee_id || ''} onChange={(event) => updateTicket({ assignee_id: Number(event.target.value) }, 'Виконавця оновлено')} className="mt-1 w-full rounded-lg border border-line bg-surface px-3 py-2 text-sm">{agents.filter((agent) => agent.role === 'agent' && agent.is_active).map((agent) => <option key={agent.id} value={agent.id}>{agent.full_name}</option>)}</select></label></div>}{ticket.status !== 'closed' && <button type="button" onClick={() => updateTicket({ status: 'closed' }, 'Звернення закрито')} className="mt-5 w-full rounded-lg border border-line px-4 py-2.5 text-xs font-semibold">Закрити звернення</button>}</aside>
    </div>
  </div>
}

export default TicketDetailPage
