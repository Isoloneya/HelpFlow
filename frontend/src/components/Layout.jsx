import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

function navLinkClass({ isActive }) {
  const base = 'rounded-md px-3.5 py-2 text-[13px] font-semibold transition-colors'
  return isActive
    ? `${base} bg-white/10 text-white`
    : `${base} text-bar-muted hover:text-white`
}

function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/')
  }

  const isStaff = user && user.role !== 'client'

  return (
    <div className="min-h-screen bg-bg text-ink">
      <header className="bg-bar text-bar-ink">
        <div className="mx-auto flex max-w-[1440px] flex-wrap items-center justify-between gap-4 px-5 py-3.5">
          <Link to="/" className="font-display text-lg font-bold">
            Help<span className="text-bar-accent">Flow</span>
          </Link>
          <nav className="flex flex-wrap items-center gap-1">
            {!user && (
              <NavLink to="/" end className={navLinkClass}>
                Вхід
              </NavLink>
            )}
            {user?.role === 'client' && (
              <NavLink to="/my-tickets" className={navLinkClass}>
                Мої звернення
              </NavLink>
            )}
            {isStaff && (
              <NavLink to="/dashboard" className={navLinkClass}>
                Дошка
              </NavLink>
            )}
            {user?.role === 'admin' && (
              <NavLink to="/categories" className={navLinkClass}>
                Категорії
              </NavLink>
            )}

            {user?.role === 'admin' && (
              <NavLink to="/agents" className={navLinkClass}>
                Агенти
              </NavLink>
            )}


            {user && (
              <>
                <span className="ml-3 max-w-[140px] truncate font-mono text-xs text-bar-muted sm:max-w-none">
                  {user.email}
                </span>
                <button
                  onClick={handleLogout}
                  className="ml-2 rounded-md border border-white/20 px-3 py-1.5 text-xs font-semibold text-bar-ink transition-colors hover:bg-white/10"
                >
                  Вийти
                </button>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-[1440px] px-5 pb-16 pt-8">{children}</main>
    </div>
  )
}

export default Layout
