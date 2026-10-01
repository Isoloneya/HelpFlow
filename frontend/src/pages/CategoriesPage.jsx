import { useEffect, useState } from 'react'
import { api } from '../api/client.js'
import { useToast } from '../context/ToastContext.jsx'

function CategoriesPage() {
  const [categories, setCategories] = useState([])
  const [name, setName] = useState('')
  const [slaHours, setSlaHours] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState('')
  const { showToast } = useToast()

  async function loadCategories() {
    try {
      setCategories(await api.get('/categories'))
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => { loadCategories() }, [])

  function openCreate() {
    setEditingId(null)
    setName('')
    setSlaHours('')
    setShowForm(true)
  }

  function openEdit(category) {
    setEditingId(category.id)
    setName(category.name)
    setSlaHours(String(category.sla_hours))
    setShowForm(true)
  }

  async function saveCategory(event) {
    event.preventDefault()
    setError('')
    try {
      if (editingId) {
        const updated = await api.patch(`/categories/${editingId}`, { name: name.trim(), sla_hours: Number(slaHours) })
        setCategories((current) => current.map((category) => category.id === editingId ? updated : category))
        showToast('Категорію оновлено')
      } else {
        const created = await api.post('/categories', { name: name.trim(), sla_hours: Number(slaHours) })
        setCategories((current) => [...current, created])
        showToast('Категорію створено')
      }
      setShowForm(false)
    } catch (err) {
      setError(err.message)
    }
  }

  async function archiveCategory(categoryId) {
    setError('')
    try {
      await api.delete(`/categories/${categoryId}`)
      await loadCategories()
      showToast('Категорію видалено або архівовано')
    } catch (err) {
      setError(err.message)
    }
  }

  return <div>
    <div className="flex flex-wrap items-end justify-between gap-4"><div><h1 className="text-2xl font-semibold">Категорії</h1><p className="mt-1 text-sm text-muted">Керуйте категоріями звернень та їхніми SLA-параметрами.</p></div><button type="button" onClick={openCreate} className="rounded-lg bg-accent px-5 py-2.5 text-xs font-semibold text-white">Додати категорію</button></div>
    {showForm && <form onSubmit={saveCategory} className="mt-6 grid gap-3 rounded-xl border border-line bg-surface p-5 shadow-sm md:grid-cols-[1fr_170px_auto_auto]"><input value={name} onChange={(event) => setName(event.target.value)} placeholder="Назва категорії" minLength="1" maxLength="100" required className="rounded-lg border border-line px-3 py-2.5 text-sm focus:border-accent focus:outline-none" /><input value={slaHours} onChange={(event) => setSlaHours(event.target.value)} placeholder="SLA, год." type="number" min="1" required className="rounded-lg border border-line px-3 py-2.5 text-sm focus:border-accent focus:outline-none" /><button type="submit" className="rounded-lg bg-accent px-5 py-2.5 text-xs font-semibold text-white">Зберегти</button><button type="button" onClick={() => setShowForm(false)} className="rounded-lg border border-line px-5 py-2.5 text-xs font-semibold">Скасувати</button></form>}
    {error && <p role="alert" className="mt-4 rounded-lg bg-[#FCE3DF] p-3 text-sm text-breach">{error}</p>}
    <div className="mt-6 overflow-x-auto rounded-xl border border-line bg-surface shadow-sm"><div className="min-w-[760px]"><div className="grid grid-cols-[1fr_160px_150px_130px_160px] gap-4 border-b border-line bg-sunken px-5 py-3 text-[11px] font-semibold uppercase tracking-wide text-muted"><span>Назва</span><span>Звернення</span><span>SLA</span><span>Статус</span><span>Дії</span></div>{categories.map((category) => <article key={category.id} className="grid grid-cols-[1fr_160px_150px_130px_160px] items-center gap-4 border-b border-line px-5 py-4 last:border-0"><p className="font-semibold">{category.name}</p><span className="font-mono text-sm">{category.ticket_count}</span><span className="text-sm">{category.sla_hours} год.</span><span className="w-fit rounded-full bg-[#E7F2EB] px-2.5 py-1 text-xs font-semibold text-ok">Активна</span><div className="flex gap-2"><button type="button" onClick={() => openEdit(category)} className="rounded-lg border border-line px-3 py-1.5 text-xs font-semibold">Змінити</button><button type="button" onClick={() => archiveCategory(category.id)} className="rounded-lg border border-[#E9B6AE] px-3 py-1.5 text-xs font-semibold text-breach">Видалити</button></div></article>)}</div></div>
  </div>
}

export default CategoriesPage
