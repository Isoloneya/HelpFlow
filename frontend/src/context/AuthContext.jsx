import { createContext, useContext, useState } from 'react'
import { api, setToken, clearToken } from '../api/client.js'

const USER_KEY = 'helpflow_user'
const AuthContext = createContext(null)

function loadStoredUser() {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(loadStoredUser)

  function persistSession(userData, token) {
    setToken(token)
    localStorage.setItem(USER_KEY, JSON.stringify(userData))
    setUser(userData)
  }

  async function login(email, password) {
    const data = await api.post('/auth/login', { email, password })
    persistSession(data.user, data.access_token)
    return data.user
  }

  async function register(email, password, role = 'client') {
    await api.post('/auth/register', { email, password, role })
    return login(email, password)
  }

  function logout() {
    clearToken()
    localStorage.removeItem(USER_KEY)
    setUser(null)
  }

  const value = { user, login, register, logout, isAuthenticated: Boolean(user) }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth має використовуватись всередині AuthProvider')
  }
  return ctx
}
