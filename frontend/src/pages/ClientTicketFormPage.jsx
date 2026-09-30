import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'

const inputClass = 'w-full rounded-lg border border-line bg-surface px-3 py-2.5 text-sm focus:border-accent focus:outline-none'

function ClientTicketFormPage() {
  const navigate = useNavigate()
  const [categories, setCategories] = useState([])
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [categoryId, setCategoryId] = useState('')
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
      const ticket = await api.post('/tickets', {
        title: title.trim(),
        description: description.trim(),
        category_id: Number(categoryId),
      })
      navigate(`/my-tickets/${ticket.id}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <Link to="/my-tickets" className="text-xs font-semibold text-accent">← Мої звернення</Link>
      <h1 className="mt-4 text-xl font-semibold">Нове звернення</h1>
      <form onSubmit={handleSubmit} className="mt-6 rounded-xl border border-line bg-surface p-5 sm:p-7">
        <label className="mb-1.5 block text-xs font-semibold text-muted">Тема</label>
        <input value={title} onChange={(event) => setTitle(event.target.value)} minLength="1" maxLength="150" required className={inputClass} />
        <label className="mb-1.5 mt-5 block text-xs font-semibold text-muted">Категорія</label>
        <select value={categoryId} onChange={(event) => setCategoryId(event.target.value)} required className={inputClass}>
          <option value="">Оберіть категорію</option>
          {categories.map((category) => <option key={category.id} value={category.id}>{category.name} · {category.sla_hours} год.</option>)}
        </select>
        <label className="mb-1.5 mt-5 block text-xs font-semibold text-muted">Опис проблеми</label>
        <textarea value={description} onChange={(event) => setDescription(event.target.value)} minLength="1" maxLength="5000" required rows="7" className={inputClass} />
        {error && <p role="alert" className="mt-4 text-sm text-breach">{error}</p>}
        <button type="submit" disabled={submitting} className="mt-6 rounded-lg bg-accent px-5 py-2.5 text-xs font-semibold text-white disabled:opacity-60">
          {submitting ? 'Створення...' : 'Надіслати звернення'}
        </button>
      </form>
    </div>
  )
}

export default ClientTicketFormPage
