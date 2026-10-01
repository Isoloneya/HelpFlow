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
    <div className="mx-auto max-w-3xl">
      <Link to="/my-tickets" className="text-xs font-semibold text-accent">← Назад до списку</Link>
      <h1 className="mt-4 text-2xl font-semibold">Створити звернення</h1>
      <p className="mt-1 text-sm text-muted">Опишіть проблему або запит, і ми допоможемо.</p>
      <form onSubmit={handleSubmit} className="mt-6 rounded-xl border border-line bg-surface p-5 sm:p-7">
        <label className="mb-1.5 block text-xs font-semibold text-muted">Тема звернення</label>
        <input value={title} onChange={(event) => setTitle(event.target.value)} minLength="1" maxLength="150" required className={inputClass} />
        <div className="mt-5 grid gap-5 sm:grid-cols-2"><div><label className="mb-1.5 block text-xs font-semibold text-muted">Категорія</label><select value={categoryId} onChange={(event) => setCategoryId(event.target.value)} required className={inputClass}><option value="">Оберіть категорію</option>{categories.map((category) => <option key={category.id} value={category.id}>{category.name} · {category.sla_hours} год.</option>)}</select></div><div className="rounded-lg bg-sunken px-4 py-3"><p className="text-xs font-semibold text-muted">Термін відповіді</p><p className="mt-1 text-sm font-semibold">Залежить від категорії</p></div></div>
        <label className="mb-1.5 mt-5 block text-xs font-semibold text-muted">Опис проблеми</label>
        <textarea value={description} onChange={(event) => setDescription(event.target.value)} minLength="1" maxLength="5000" required rows="7" className={inputClass} />
        {error && <p role="alert" className="mt-4 text-sm text-breach">{error}</p>}
        <div className="mt-6 flex justify-end"><button type="submit" disabled={submitting} className="rounded-lg bg-accent px-5 py-2.5 text-xs font-semibold text-white disabled:opacity-60">{submitting ? 'Створення...' : 'Створити звернення'}</button></div>
      </form>
    </div>
  )
}

export default ClientTicketFormPage
