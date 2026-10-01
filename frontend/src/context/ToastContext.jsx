import { createContext, useContext, useState } from 'react'

const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [message, setMessage] = useState('')

  function showToast(nextMessage) {
    setMessage(nextMessage)
    window.setTimeout(() => setMessage(''), 3000)
  }

  return <ToastContext.Provider value={{ showToast }}>{children}{message && <div role="status" className="fixed bottom-5 right-5 z-50 rounded-lg bg-bar px-4 py-3 text-sm font-semibold text-white shadow-xl">{message}</div>}</ToastContext.Provider>
}

export function useToast() {
  return useContext(ToastContext)
}
