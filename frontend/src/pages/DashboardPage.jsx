import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

const STATUS_LABELS = {
  uploaded: { label: 'Enviado', class: 'status-uploaded', icon: '📤' },
  processing: { label: 'Processando', class: 'status-processing', icon: '⏳' },
  analyzed: { label: 'Analisado', class: 'status-analyzed', icon: '✅' },
  error: { label: 'Erro', class: 'status-error', icon: '❌' },
}

export default function DashboardPage() {
  const [patients, setPatients] = useState([])
  const [exams, setExams] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [selectedPatient, setSelectedPatient] = useState(null)
  const [patientExams, setPatientExams] = useState([])
  const [loadingExams, setLoadingExams] = useState(false)
  const [reanalyzingId, setReanalyzingId] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    setError('')
    try {
      const [patientsRes, examsRes] = await Promise.all([
        api.get('/patients/'),
        api.get('/exams/'),
      ])
      setPatients(patientsRes.data)
      setExams(examsRes.data)
    } catch (err) {
      setError('Não foi possível carregar os dados. Verifique sua conexão.')
    } finally {
      setLoading(false)
    }
  }

  const loadPatientExams = async (patient) => {
    setSelectedPatient(patient)
    setLoadingExams(true)
    try {
      const res = await api.get(`/patients/${patient.id}/exams`)
      setPatientExams(res.data)
    } catch {
      setPatientExams([])
    } finally {
      setLoadingExams(false)
    }
  }

  const filteredPatients = patients.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase())
  )

  const stats = {
    total: exams.length,
    analyzed: exams.filter(e => e.status === 'analyzed').length,
    uploaded: exams.filter(e => e.status === 'uploaded').length,
    error: exams.filter(e => e.status === 'error').length,
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading-container">
          <div className="spinner" />
          <p>Carregando dados...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      {error && <div className="alert alert-error">{error}</div>}

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number">{stats.total}</div>
          <div className="stat-label">Total de Exames</div>
        </div>
        <div className="stat-card stat-success">
          <div className="stat-number">{stats.analyzed}</div>
          <div className="stat-label">Analisados</div>
        </div>
        <div className="stat-card stat-warning">
          <div className="stat-number">{stats.uploaded}</div>
          <div className="stat-label">Aguardando Análise</div>
        </div>
        <div className="stat-card stat-danger">
          <div className="stat-number">{stats.error}</div>
          <div className="stat-label">Com Erro</div>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Patients List */}
        <div className="card">
          <div className="card-header">
            <h2>👥 Pacientes</h2>
            <span className="badge">{filteredPatients.length}</span>
          </div>

          <div className="form-group" style={{ marginBottom: 12 }}>
            <input
              type="text"
              placeholder="🔍 Buscar paciente..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          {filteredPatients.length === 0 ? (
            <p className="empty-state">
              {search ? 'Nenhum paciente encontrado' : 'Nenhum paciente cadastrado'}
            </p>
          ) : (
            <div className="patient-list">
              {filteredPatients.map(patient => (
                <div
                  key={patient.id}
                  className={`patient-item ${selectedPatient?.id === patient.id ? 'active' : ''}`}
                  onClick={() => loadPatientExams(patient)}
                >
                  <div className="patient-name">{patient.name}</div>
                  <div className="patient-date">{formatDate(patient.created_at)}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Exam History */}
        <div className="card">
          <div className="card-header">
            <h2>📋 {selectedPatient ? `Exames de ${selectedPatient.name}` : 'Todos os Exames'}</h2>
            {selectedPatient && (
              <button className="btn-link" onClick={() => { setSelectedPatient(null); setPatientExams([]) }}>
                Ver todos
              </button>
            )}
          </div>

          {loadingExams ? (
            <div className="loading-container">
              <div className="spinner" />
              <p>Carregando exames...</p>
            </div>
          ) : (
            <div className="exam-list">
              {(selectedPatient ? patientExams : exams).length === 0 ? (
                <p className="empty-state">Nenhum exame encontrado</p>
              ) : (
                (selectedPatient ? patientExams : exams).map(exam => {
                  const st = STATUS_LABELS[exam.status] || STATUS_LABELS.uploaded
                  const patientName = selectedPatient
                    ? selectedPatient.name
                    : patients.find(p => p.id === exam.patient_id)?.name || '-'
                  return (
                    <div key={exam.id} className="exam-item">
                      <div className="exam-item-main">
                        <div className="exam-item-info">
                          <span className="exam-file">{st.icon} {exam.file_name || 'Exame'}</span>
                          {!selectedPatient && (
                            <span className="exam-patient">{patientName}</span>
                          )}
                        </div>
                        <div className="exam-item-meta">
                          <span className={`status-badge ${st.class}`}>{st.label}</span>
                          <span className="exam-date">{formatDate(exam.created_at)}</span>
                        </div>
                      </div>
                      <div className="exam-item-actions">
                        {(exam.status === 'analyzed' || exam.status === 'processing') && (
                          <button
                            className="btn btn-sm"
                            onClick={() => navigate(`/report/${exam.id}`)}
                          >
                            📝 Ver Laudo
                          </button>
                        )}
                        {(exam.status === 'processing' || exam.status === 'error') && (
                          <button
                            className="btn btn-sm btn-outline"
                            disabled={reanalyzingId === exam.id}
                            onClick={async () => {
                              setReanalyzingId(exam.id)
                              try {
                                await api.post(`/exams/${exam.id}/analyze`)
                                await loadData()
                              } catch (err) {
                                alert(err.response?.data?.detail || 'Erro ao reanalisar')
                              } finally {
                                setReanalyzingId(null)
                              }
                            }}
                          >
                            {reanalyzingId === exam.id ? (
                              <><span className="spinner-sm" /> Analisando...</>
                            ) : (
                              '🔄 Reanalisar'
                            )}
                          </button>
                        )}
                        {exam.status === 'uploaded' && (
                          <span className="text-muted">Aguardando análise</span>
                        )}
                      </div>
                    </div>
                  )
                })
              )}
            </div>
          )}
        </div>
      </div>

      {/* Quick action */}
      <div style={{ textAlign: 'center', marginTop: 20 }}>
        <button className="btn btn-lg" onClick={() => navigate('/upload')}>
          ➕ Novo Exame
        </button>
      </div>
    </div>
  )
}
