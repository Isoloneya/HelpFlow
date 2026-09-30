import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext.jsx'
import RequireAuth from './context/RequireAuth.jsx'
import Layout from './components/Layout.jsx'
import AuthPage from './pages/AuthPage.jsx'
import ClientDashboardPage from './pages/ClientDashboardPage.jsx'
import OperatorBoardPage from './pages/OperatorBoardPage.jsx'
import ClientTicketFormPage from './pages/ClientTicketFormPage.jsx'
import TicketDetailPage from './pages/TicketDetailPage.jsx'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<AuthPage />} />
            <Route
              path="/my-tickets"
              element={
                <RequireAuth roles={['client']}>
                  <ClientDashboardPage />
                </RequireAuth>
              }
            />
            <Route
              path="/my-tickets/new"
              element={
                <RequireAuth roles={['client']}>
                  <ClientTicketFormPage />
                </RequireAuth>
              }
            />
            <Route
              path="/my-tickets/:id"
              element={
                <RequireAuth roles={['client']}>
                  <TicketDetailPage />
                </RequireAuth>
              }
            />
            <Route
              path="/dashboard"
              element={
                <RequireAuth roles={['agent', 'admin']}>
                  <OperatorBoardPage />
                </RequireAuth>
              }
            />
            <Route
              path="/tickets/:id"
              element={
                <RequireAuth roles={['agent', 'admin']}>
                  <TicketDetailPage />
                </RequireAuth>
              }
            />
          </Routes>
        </Layout>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
