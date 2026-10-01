import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

const HERO = {
  client: {
    title: 'Слідкуйте за своїми зверненнями в одному місці',
    text: 'Створюйте звернення, стежте за статусом і отримуйте відповідь від команди підтримки, не чекаючи на пошту.',
  },
  operator: {
    title: 'Робочий простір для команди підтримки',
    text: 'Дошка звернень, автоматичний розподіл навантаження та контроль SLA в одному місці.',
  },
}

const inputClass =
  'w-full rounded-lg border border-line bg-surface px-3 py-2.5 text-base focus:border-accent focus:outline-none sm:text-[13px]'

function AuthPage() {
  const { user, login, register, logout } = useAuth()
  const navigate = useNavigate()

  const [role, setRole] = useState('client')
  const [mode, setMode] = useState('signin')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [registrationRole, setRegistrationRole] = useState('agent')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (user) {
    return <Navigate to={user.role === 'client' ? '/my-tickets' : '/dashboard'} replace />
  }

  const hero = HERO[role]
  const isOperatorSignup = role === 'operator' && mode === 'signup'

  function switchRole(nextRole) {
    setRole(nextRole)
    setError('')
  }

  function switchMode(nextMode) {
    setMode(nextMode)
    setError('')
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (mode === 'signup') {
      if (password.length < 8) {
        setError('Пароль має містити щонайменше 8 символів')
        return
      }
      if (password !== confirm) {
        setError('Паролі не збігаються')
        return
      }
    }

    setSubmitting(true)
    try {
      const account = mode === 'signin'
        ? await login(email, password)
        : await register(email, password, role === 'operator' ? registrationRole : 'client')
      const isOperatorAccount = account.role !== 'client'

      if (role === 'operator' && !isOperatorAccount) {
        logout()
        setError('Цей акаунт не має доступу оператора. Увійдіть як клієнт.')
        return
      }
      if (role === 'client' && isOperatorAccount) {
        logout()
        setError('Це акаунт оператора. Оберіть вкладку "Оператор".')
        return
      }

      navigate(isOperatorAccount ? '/dashboard' : '/my-tickets')
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto grid max-w-[840px] overflow-hidden rounded-2xl border border-line md:grid-cols-2">
      <div className="flex flex-col justify-center bg-bar p-6 text-bar-ink md:p-9">
        <h1 className="text-xl font-semibold leading-tight md:text-2xl">{hero.title}</h1>
        <p className="mt-3 text-[13px] leading-relaxed text-bar-muted">{hero.text}</p>
      </div>

      <div className="bg-surface p-6 md:p-8">
        <div className="mb-5 grid grid-cols-2 gap-2">
          {[
            ['client', 'Клієнт'],
            ['operator', 'Оператор'],
          ].map(([value, label]) => (
            <button
              key={value}
              type="button"
              onClick={() => switchRole(value)}
              className={`rounded-lg border py-2.5 text-xs font-semibold ${
                role === value
                  ? 'border-ink bg-ink text-white'
                  : 'border-line bg-surface text-muted'
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <div className="mb-5 flex gap-5 border-b border-line">
          {[
            ['signin', 'Увійти'],
            ['signup', 'Реєстрація'],
          ].map(([value, label]) => (
            <button
              key={value}
              type="button"
              onClick={() => switchMode(value)}
              className={`border-b-2 pb-2.5 text-[13px] font-semibold ${
                mode === value ? 'border-accent text-ink' : 'border-transparent text-muted'
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit}>
            <div className="mb-3.5">
              <label className="mb-1.5 block text-xs font-semibold text-muted">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                required
                className={inputClass}
              />
            </div>
            <div className="mb-3.5">
              <label className="mb-1.5 block text-xs font-semibold text-muted">Пароль</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete={mode === 'signin' ? 'current-password' : 'new-password'}
                required
                className={inputClass}
              />
            </div>
            {mode === 'signup' && (
              <>
                {isOperatorSignup && <div className="mb-3.5"><label className="mb-1.5 block text-xs font-semibold text-muted">Роль у демо</label><select value={registrationRole} onChange={(event) => setRegistrationRole(event.target.value)} className={inputClass}><option value="agent">Агент</option><option value="admin">Адміністратор</option></select><p className="mt-1.5 text-[11px] text-muted">Доступно лише коли на backend увімкнено демо-режим.</p></div>}
                <div className="mb-3.5">
                <label className="mb-1.5 block text-xs font-semibold text-muted">
                  Підтвердження пароля
                </label>
                <input
                  type="password"
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  autoComplete="new-password"
                  required
                  className={inputClass}
                />
                <p className="mt-1.5 text-[11px] text-muted">Мінімум 8 символів</p>
                </div>
              </>
            )}
            {error && (
              <p role="alert" className="mb-3.5 text-[13px] text-breach">
                {error}
              </p>
            )}
            <button
              type="submit"
              disabled={submitting}
              className="w-full rounded-lg bg-accent py-3 text-[13px] font-semibold text-white disabled:opacity-60"
            >
              {submitting ? 'Зачекайте...' : mode === 'signin' ? 'Увійти' : 'Створити акаунт'}
            </button>
          </form>
      </div>
    </div>
  )
}

export default AuthPage
