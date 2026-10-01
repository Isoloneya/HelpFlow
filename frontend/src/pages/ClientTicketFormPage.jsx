import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { api } from '../api/client.js'
import { useToast } from '../context/ToastContext.jsx'

const inputClass = 'w-full rounded-lg border border-line bg-surface px-3 py-2.5 text-sm focus:border-accent focus:outline-none'

function ClientTicketFormPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const followUpId = searchParams.get('follow_up_of')
  const { showToast } = useToast()
  const [categories, setCategories] = useState([])
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [priority, setPriority] = useState('medium')
  const [files, setFiles] = useState([])
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    api.get('/categories').then(setCategories).catch((err) => setError(err.message))
  }, [])

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    if (!categoryId) {
      setError('Оберіть категорію')
      return
    }
    setSubmitting(true)
    try {
      const formData = new FormData()
      formData.append('title', title.trim())
      formData.append('description', description.trim())
      formData.append('category_id', categoryId)
      formData.append('priority', priority)
      if (followUpId) formData.append('parent_ticket_id', followUpId)
      files.forEach((file) => formData.append('files', file))
      const ticket = await api.postForm('/tickets', formData)
      showToast('Звернення створено')
      navigate(`/my-tickets/${ticket.id}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-[920px]">
      <Link to="/my-tickets" className="text-xs font-semibold text-accent">← Назад</Link>
      <h1 className="mt-3 text-2xl font-semibold">Створити звернення</h1>
      <p className="mt-1 text-sm text-muted">Опишіть вашу проблему або запит, і ми допоможемо.</p>
      {followUpId && <p className="mt-3 rounded-lg bg-[#FFF1D7] px-3 py-2 text-xs text-risk">Повторне звернення до #{followUpId}</p>}
      <form onSubmit={handleSubmit} className="mt-4 rounded-xl border border-line bg-surface p-5 shadow-sm">
        <label className="mb-1.5 block text-xs font-semibold text-muted">Тема звернення <span className="text-breach">*</span></label>
        <input value={title} onChange={(event) => setTitle(event.target.value)} minLength="1" maxLength="150" required className={inputClass} />
        <div className="mt-5 grid gap-4 sm:grid-cols-2"><div><label className="mb-1.5 block text-xs font-semibold text-muted">Категорія <span className="text-breach">*</span></label><select value={categoryId} onChange={(event) => setCategoryId(event.target.value)} required className={inputClass}><option value="">Оберіть категорію</option>{categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select></div><div><label className="mb-1.5 block text-xs font-semibold text-muted">Пріоритет <span className="text-breach">*</span></label><select value={priority} onChange={(event) => setPriority(event.target.value)} className={inputClass}><option value="low">low</option><option value="medium">medium</option><option value="high">high</option><option value="urgent">urgent</option></select></div></div>
        <label className="mb-1.5 mt-5 block text-xs font-semibold text-muted">Опис <span className="text-breach">*</span></label>
        <textarea value={description} onChange={(event) => setDescription(event.target.value)} minLength="1" maxLength="5000" required rows="5" className={inputClass} />
        <label className="mb-1.5 mt-5 block text-xs font-semibold text-muted">Додати файли</label>
        <label className="flex cursor-pointer items-center justify-center gap-3 rounded-lg border border-dashed border-line bg-[#FCFDFC] px-4 py-5 text-center text-xs text-muted hover:border-accent">
          <span className="text-lg text-ink">⌕</span><span>Перетягніть файли сюди або <span className="font-semibold text-accent">натисніть для вибору</span></span>
          <input type="file" multiple className="sr-only" onChange={(event) => setFiles(Array.from(event.target.files || []))} />
        </label>
        <p className="mt-1.5 text-[11px] text-muted">Максимальний розмір файлу — 10 МБ. Можна додати кілька файлів.</p>
        {files.length > 0 && <p className="mt-2 text-xs text-ink">{files.map((file) => file.name).join(', ')}</p>}
        {error && <p role="alert" className="mt-4 text-sm text-breach">{error}</p>}
        <div className="mt-6 flex items-center justify-between"><Link to="/my-tickets" className="rounded-lg bg-sunken px-5 py-2.5 text-xs font-semibold text-ink">Скасувати</Link><button type="submit" disabled={submitting} className="rounded-lg bg-accent px-5 py-2.5 text-xs font-semibold text-white disabled:opacity-60">{submitting ? 'Створення...' : 'Створити звернення'}</button></div>
      </form>
    </div>
  )
}

export default ClientTicketFormPage
