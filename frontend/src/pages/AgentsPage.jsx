import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { api } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'
import { useToast } from '../context/ToastContext.jsx'

const roleLabels = { agent: 'Агент', admin: 'Адміністратор' }

function AgentsPage() {
  const [agents, setAgents] = useState([])
  const [categories, setCategories] = useState([])
  const [selectedCategoryIds, setSelectedCategoryIds] = useState([])
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [temporaryPassword, setTemporaryPassword] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [openActions, setOpenActions] = useState(null)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const { user } = useAuth()
  const { showToast } = useToast()

  async function loadAgents() {
    try {
      setAgents(await api.get('/users'))
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => { loadAgents() }, [])
  useEffect(() => { api.get('/categories').then(setCategories).catch((err) => setError(err.message)) }, [])

  async function createAgent(event) {
    event.preventDefault()
    setError('')
    setTemporaryPassword('')
    setSubmitting(true)
    try {
      const agent = await api.post('/users', { full_name: fullName.trim(), email: email.trim() })
      setAgents((current) => [...current, agent])
      setTemporaryPassword(agent.temporary_password)
      setFullName('')
      setEmail('')
      setShowForm(false)
      showToast('Агента створено')
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function updateAgent(agentId, data) {
    setError('')
    try {
      const updated = await api.patch(`/users/${agentId}`, data)
      setAgents((current) => current.map((agent) => (agent.id === agentId ? updated : agent)))
      setOpenActions(null)
      showToast('Дані працівника оновлено')
    } catch (err) {
      setError(err.message)
    }
  }

  async function deleteAgent(agentId) {
    setError('')
    try {
      await api.delete(`/users/${agentId}`)
      setAgents((current) => current.filter((agent) => agent.id !== agentId))
      setOpenActions(null)
      showToast('Працівника видалено')
    } catch (err) {
      setError(err.message)
    }
  }

  function toggleActions(event, agent) {
    const bounds = event.currentTarget.getBoundingClientRect()
    setSelectedCategoryIds(agent.category_ids)
    setOpenActions((current) => current?.id === agent.id ? null : { id: agent.id, top: bounds.bottom + 6, left: bounds.right - 208 })
  }

  const activeAgent = agents.find((agent) => agent.id === openActions?.id)

  return <div>
    <div className="flex flex-wrap items-end justify-between gap-4"><div><h1 className="text-2xl font-semibold">Агенти</h1><p className="mt-1 text-sm text-muted">Керуйте командою підтримки та її правами доступу.</p></div><button type="button" onClick={() => setShowForm((value) => !value)} className="rounded-lg bg-accent px-5 py-2.5 text-xs font-semibold text-white">Додати агента</button></div>
    {showForm && <form onSubmit={createAgent} className="mt-6 grid gap-3 rounded-xl border border-line bg-surface p-5 shadow-sm md:grid-cols-[1fr_1fr_auto]"><input value={fullName} onChange={(event) => setFullName(event.target.value)} placeholder="Повне ім’я" minLength="2" maxLength="120" required className="rounded-lg border border-line px-3 py-2.5 text-sm focus:border-accent focus:outline-none" /><input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="email@company.com" type="email" required className="rounded-lg border border-line px-3 py-2.5 text-sm focus:border-accent focus:outline-none" /><button type="submit" disabled={submitting} className="rounded-lg bg-accent px-5 py-2.5 text-xs font-semibold text-white disabled:opacity-60">{submitting ? 'Створення...' : 'Створити'}</button></form>}
    {temporaryPassword && <div className="mt-4 rounded-xl border border-[#E9C98E] bg-[#FFF1D7] p-4"><p className="text-xs font-semibold text-risk">Тимчасовий пароль нового агента</p><p className="mt-2 font-mono text-sm font-semibold">{temporaryPassword}</p></div>}
    {error && <p role="alert" className="mt-4 rounded-lg bg-[#FCE3DF] p-3 text-sm text-breach">{error}</p>}
    <div className="mt-6 overflow-x-auto rounded-xl border border-line bg-surface shadow-sm"><div className="min-w-[800px]"><div className="grid grid-cols-[1.2fr_1.5fr_150px_130px_100px_50px] gap-4 border-b border-line bg-sunken px-5 py-3 text-[11px] font-semibold uppercase tracking-wide text-muted"><span>Ім’я</span><span>Email</span><span>Роль</span><span>Статус</span><span>Звернень</span><span></span></div>{agents.map((agent) => <article key={agent.id} className="grid grid-cols-[1.2fr_1.5fr_150px_130px_100px_50px] items-center gap-4 border-b border-line px-5 py-4 last:border-0"><p className="font-semibold">{agent.full_name === 'Користувач' ? agent.email.split('@')[0] : agent.full_name}</p><p className="truncate text-sm text-muted">{agent.email}</p><span className={`w-fit rounded-full px-2.5 py-1 text-xs font-semibold ${agent.role === 'admin' ? 'bg-[#EEE9FF] text-[#6753B6]' : 'bg-[#E5F0FF] text-[#3971B9]'}`}>{roleLabels[agent.role]}</span><span className={`w-fit rounded-full px-2.5 py-1 text-xs font-semibold ${agent.is_active ? 'bg-[#E7F2EB] text-ok' : 'bg-[#FCE3DF] text-breach'}`}>{agent.is_active ? 'Активний' : 'Неактивний'}</span><span className="font-mono text-sm">{agent.active_ticket_count}</span><button type="button" onClick={(event) => toggleActions(event, agent)} className="rounded-lg px-2 py-1 text-lg font-semibold text-muted">•••</button></article>)}</div></div>
    {activeAgent && createPortal(<div className="fixed z-50 grid w-52 gap-1 rounded-lg border border-line bg-surface p-2 shadow-lg" style={{ top: openActions.top, left: openActions.left }}><p className="px-2 pt-1 text-[11px] font-semibold uppercase text-muted">Категорії агента</p><div className="max-h-32 overflow-y-auto">{categories.map((category) => <label key={category.id} className="flex cursor-pointer items-center gap-2 rounded px-2 py-1.5 text-xs hover:bg-sunken"><input type="checkbox" checked={selectedCategoryIds.includes(category.id)} onChange={(event) => setSelectedCategoryIds((current) => event.target.checked ? [...current, category.id] : current.filter((id) => id !== category.id))} />{category.name}</label>)}</div><button type="button" onClick={() => updateAgent(activeAgent.id, { category_ids: selectedCategoryIds })} disabled={activeAgent.id === user.id} className="rounded bg-sunken px-2 py-1.5 text-left text-xs font-semibold disabled:cursor-not-allowed disabled:opacity-50">Зберегти категорії</button><div className="my-1 border-t border-line"></div><button type="button" onClick={() => updateAgent(activeAgent.id, { role: activeAgent.role === 'agent' ? 'admin' : 'agent' })} disabled={activeAgent.id === user.id} className="rounded px-2 py-1.5 text-left text-xs hover:bg-sunken disabled:cursor-not-allowed disabled:opacity-50">Змінити роль</button><button type="button" onClick={() => updateAgent(activeAgent.id, { is_active: !activeAgent.is_active })} disabled={activeAgent.id === user.id} className="rounded px-2 py-1.5 text-left text-xs hover:bg-sunken disabled:cursor-not-allowed disabled:opacity-50">{activeAgent.is_active ? 'Деактивувати' : 'Активувати'}</button><button type="button" onClick={() => deleteAgent(activeAgent.id)} disabled={activeAgent.id === user.id} className="rounded px-2 py-1.5 text-left text-xs text-breach hover:bg-[#FCE3DF] disabled:cursor-not-allowed disabled:opacity-50">Видалити</button></div>, document.body)}
  </div>
}

export default AgentsPage
