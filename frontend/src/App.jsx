import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate, NavLink } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import UploadPage from './pages/UploadPage'
import DashboardPage from './pages/DashboardPage'
import ReportPage from './pages/ReportPage'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(
    () => !!localStorage.getItem('token')
  )

  const handleLogin = () => setIsAuthenticated(true)

  const handleLogout = () => {
    localStorage.removeItem('token')
    setIsAuthenticated(false)
  }

  return (
    <BrowserRouter>
      {isAuthenticated && (
        <div className="header">
          <h1>🧠 Sistema de Laudos EEG</h1>
          <nav className="header-nav">
            <NavLink to="/" end>Painel</NavLink>
            <NavLink to="/upload">Novo Exame</NavLink>
          </nav>
          <button onClick={handleLogout}>Sair</button>
        </div>
      )}
      <Routes>
        <Route
          path="/login"
          element={
            isAuthenticated
              ? <Navigate to="/" />
              : <LoginPage onLogin={handleLogin} />
          }
        />
        <Route
          path="/"
          element={
            isAuthenticated
              ? <DashboardPage />
              : <Navigate to="/login" />
          }
        />
        <Route
          path="/upload"
          element={
            isAuthenticated
              ? <UploadPage />
              : <Navigate to="/login" />
          }
        />
        <Route
          path="/report/:examId"
          element={
            isAuthenticated
              ? <ReportPage />
              : <Navigate to="/login" />
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
