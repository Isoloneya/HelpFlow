import { useEffect, useState } from 'react'
import { api } from '../api/client.js'
import { useToast } from '../context/ToastContext.jsx'

const roleLabels = { client: 'Клієнт', agent: 'Агент підтримки', admin: 'Адміністратор' }

function ProfilePage() {
  const { showToast } = useToast()
  const [profile, setProfile] = useState(null)
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    api.get('/auth/me').then((data) => { setProfile(data); setFullName(data.full_name) }).catch((err) => setError(err.message))
  }, [])

  async function saveProfile(event) {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      const updated = await api.patch('/auth/me', { full_name: fullName.trim() })
      setProfile(updated)
      showToast('Профіль оновлено')
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  if (error && !profile) return <p role="alert" className="rounded-lg bg-[#FCE3DF] p-3 text-sm text-breach">{error}</p>
  if (!profile) return <p className="text-sm text-muted">Завантаження...</p>

  return <div className="mx-auto max-w-2xl"><h1 className="text-2xl font-semibold">Профіль</h1><p className="mt-1 text-sm text-muted">Дані вашого облікового запису.</p><section className="mt-6 rounded-xl border border-line bg-surface p-5 shadow-sm sm:p-7"><form onSubmit={saveProfile}><label className="text-xs font-semibold uppercase tracking-wide text-muted">Ім’я<input value={fullName} onChange={(event) => setFullName(event.target.value)} minLength="2" maxLength="120" required className="mt-2 block w-full rounded-lg border border-line px-3 py-2.5 text-sm" /></label><button type="submit" disabled={saving} className="mt-4 rounded-lg bg-accent px-4 py-2.5 text-xs font-semibold text-white disabled:opacity-60">{saving ? 'Збереження...' : 'Зберегти'}</button></form>{error && <p role="alert" className="mt-4 text-sm text-breach">{error}</p>}<div className="mt-7 grid gap-5 border-t border-line pt-5 sm:grid-cols-2"><div><p className="text-xs font-semibold uppercase tracking-wide text-muted">Email</p><p className="mt-2 text-sm font-semibold">{profile.email}</p></div><div><p className="text-xs font-semibold uppercase tracking-wide text-muted">Роль</p><p className="mt-2 text-sm font-semibold">{roleLabels[profile.role]}</p></div><div><p className="text-xs font-semibold uppercase tracking-wide text-muted">Створено</p><p className="mt-2 text-sm font-semibold">{new Date(profile.created_at).toLocaleString('uk-UA')}</p></div></div></section></div>
}

export default ProfilePage
