import { useEffect, useState } from 'react'
import { api } from '../api/client.js'

function CategoriesPage() {
  const [categories, setCategories] = useState([])
  const [name, setName] = useState('')
  const [slaHours, setSlaHours] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [editName, setEditName] = useState('')
  const [editSlaHours, setEditSlaHours] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function loadCategories() {
    try {
      const data = await api.get('/categories')
      setCategories(data)
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    loadCategories()
  }, [])

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)

    try {
      const category = await api.post('/categories', {
        name: name.trim(),
        sla_hours: Number(slaHours),
      })

      setCategories((current) =>
        [...current, category].sort((first, second) =>
          first.name.localeCompare(second.name, 'uk-UA'),
        ),
      )
      setName('')
      setSlaHours('')
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  function startEditing(category) {
    setEditingId(category.id)
    setEditName(category.name)
    setEditSlaHours(String(category.sla_hours))
    setError('')
  }

  function cancelEditing() {
    setEditingId(null)
    setEditName('')
    setEditSlaHours('')
  }

  async function saveCategory(categoryId) {
    setError('')

    try {
      const updated = await api.patch(`/categories/${categoryId}`, {
        name: editName.trim(),
        sla_hours: Number(editSlaHours),
      })

      setCategories((current) =>
        current
          .map((category) => (category.id === categoryId ? updated : category))
          .sort((first, second) => first.name.localeCompare(second.name, 'uk-UA')),
      )
      cancelEditing()
    } catch (err) {
      setError(err.message)
    }
  }

  async function deleteCategory(categoryId) {
    setError('')

    try {
      await api.delete(`/categories/${categoryId}`)
      await loadCategories()
      cancelEditing()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold">Категорії</h1>
      <p className="mt-1 text-sm text-muted">Керування категоріями та термінами SLA.</p>

      <form
        onSubmit={handleSubmit}
        className="mt-6 grid gap-3 rounded-xl border border-line bg-surface p-5 sm:grid-cols-[1fr_150px_auto]"
      >
        <input
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="Назва категорії"
          minLength="1"
          maxLength="100"
          required
          className="rounded-lg border border-line px-3 py-2.5 text-sm focus:border-accent focus:outline-none"
        />
        <input
          value={slaHours}
          onChange={(event) => setSlaHours(event.target.value)}
          placeholder="SLA, год."
          type="number"
          min="1"
          required
          className="rounded-lg border border-line px-3 py-2.5 text-sm focus:border-accent focus:outline-none"
        />
        <button
          type="submit"
          disabled={submitting}
          className="rounded-lg bg-accent px-5 py-2.5 text-xs font-semibold text-white disabled:opacity-60"
        >
          {submitting ? 'Створення...' : 'Додати'}
        </button>
      </form>

      {error && (
        <p role="alert" className="mt-4 rounded-lg bg-[#FCE3DF] p-3 text-sm text-breach">
          {error}
        </p>
      )}

      <div className="mt-6 overflow-hidden rounded-xl border border-line bg-surface">
        <div className="hidden grid-cols-[1fr_160px_220px] gap-4 border-b border-line bg-sunken px-5 py-3 text-[11px] font-semibold uppercase tracking-wide text-muted sm:grid"><span>Назва</span><span>SLA</span><span>Керування</span></div>
        {categories.map((category) => (
          <article key={category.id} className="border-b border-line p-4 last:border-0 sm:px-5">
            {editingId === category.id ? (
              <div className="grid gap-3 sm:grid-cols-[1fr_130px_auto_auto]">
                <input
                  value={editName}
                  onChange={(event) => setEditName(event.target.value)}
                  minLength="1"
                  maxLength="100"
                  className="rounded-lg border border-line px-3 py-2 text-sm focus:border-accent focus:outline-none"
                />
                <input
                  value={editSlaHours}
                  onChange={(event) => setEditSlaHours(event.target.value)}
                  type="number"
                  min="1"
                  className="rounded-lg border border-line px-3 py-2 text-sm focus:border-accent focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => saveCategory(category.id)}
                  className="rounded-lg bg-accent px-4 py-2 text-xs font-semibold text-white"
                >
                  Зберегти
                </button>
                <button
                  type="button"
                  onClick={cancelEditing}
                  className="rounded-lg border border-line px-4 py-2 text-xs font-semibold"
                >
                  Скасувати
                </button>
              </div>
            ) : (
              <div className="flex flex-wrap items-center justify-between gap-3 sm:grid sm:grid-cols-[1fr_160px_220px] sm:gap-4">
                <div>
                  <p className="font-semibold">{category.name}</p>
                </div>
                <p className="text-xs text-muted">{category.sla_hours} год.</p>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => startEditing(category)}
                    className="rounded-lg border border-line px-3 py-2 text-xs font-semibold"
                  >
                    Змінити
                  </button>
                  <button
                    type="button"
                    onClick={() => deleteCategory(category.id)}
                    className="rounded-lg border border-[#E9B6AE] px-3 py-2 text-xs font-semibold text-breach"
                  >
                    Видалити
                  </button>
                </div>
              </div>
            )}
          </article>
        ))}
      </div>
    </div>
  )
}

export default CategoriesPage
