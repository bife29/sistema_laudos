import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

const ERROR_MESSAGES = {
  'Erro no upload': 'Não foi possível enviar o arquivo. Verifique sua conexão e tente novamente.',
  'Erro na análise': 'A análise do exame falhou. O arquivo pode estar corrompido ou em formato incompatível.',
  'Erro ao gerar laudo': 'Não foi possível gerar o laudo. Tente novamente em alguns instantes.',
}

export default function UploadPage() {
  const [file, setFile] = useState(null)
  const [patientName, setPatientName] = useState('')
  const [indication, setIndication] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const [step, setStep] = useState('upload') // upload | analyzing | done
  const [uploading, setUploading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [examResult, setExamResult] = useState(null)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [report, setReport] = useState(null)
  const [error, setError] = useState('')
  const fileRef = useRef()
  const navigate = useNavigate()

  const friendlyError = (err, fallback) => {
    const msg = err.response?.data?.detail || fallback
    return ERROR_MESSAGES[msg] || msg
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped && dropped.name.toLowerCase().endsWith('.edf')) {
      setFile(dropped)
    } else {
      setError('Por favor, envie um arquivo .EDF')
    }
  }

  const handleFileSelect = (e) => {
    const selected = e.target.files[0]
    if (selected) setFile(selected)
  }

  const handleUpload = async () => {
    if (!file || !patientName) {
      setError('Preencha o nome do paciente e selecione o arquivo')
      return
    }
    setError('')
    setUploading(true)

    try {
      // 1. Criar paciente
      const patientRes = await api.post('/patients/', {
        name: patientName,
      })
      const patientId = patientRes.data.id

      // 2. Upload do arquivo
      const formData = new FormData()
      formData.append('file', file)
      formData.append('patient_id', patientId)
      formData.append('indication', indication)

      const uploadRes = await api.post('/exams/upload', formData)
      setExamResult(uploadRes.data)
    } catch (err) {
      setError(friendlyError(err, 'Erro no upload'))
    } finally {
      setUploading(false)
    }
  }

  const handleAnalyze = async () => {
    if (!examResult) return
    setAnalyzing(true)
    setError('')

    try {
      const res = await api.post(`/exams/${examResult.exam_id}/analyze`)
      setAnalysisResult(res.data)
    } catch (err) {
      setError(friendlyError(err, 'Erro na análise'))
    } finally {
      setAnalyzing(false)
    }
  }

  const handleGenerateReport = async () => {
    if (!examResult) return
    setGenerating(true)
    setError('')

    try {
      const res = await api.post(`/exams/${examResult.exam_id}/generate-report`)
      setReport(res.data)
    } catch (err) {
      setError(friendlyError(err, 'Erro ao gerar laudo'))
    } finally {
      setGenerating(false)
    }
  }

  const handleNewConsult = () => {
    setFile(null)
    setPatientName('')
    setIndication('')
    setExamResult(null)
    setAnalysisResult(null)
    setReport(null)
    setError('')
    if (fileRef.current) fileRef.current.value = ''
  }

  return (
    <div className="container">
      {/* STEP 1: Upload */}
      <div className="card">
        <h2>📤 Enviar Exame EEG</h2>

        <div className="form-group">
          <label>Nome do Paciente *</label>
          <input
            type="text"
            value={patientName}
            onChange={(e) => setPatientName(e.target.value)}
            placeholder="Ex: Isaac Gomes Bueno"
          />
        </div>

        <div className="form-group">
          <label>Indicação</label>
          <input
            type="text"
            value={indication}
            onChange={(e) => setIndication(e.target.value)}
            placeholder="Ex: Crises convulsivas"
          />
        </div>

        <div
          className={`upload-area ${dragOver ? 'drag-over' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileRef.current?.click()}
        >
          <input
            ref={fileRef}
            type="file"
            accept=".edf"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          {file ? (
            <>
              <p style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>📄 {file.name}</p>
              <p>{(file.size / (1024 * 1024)).toFixed(1)} MB</p>
            </>
          ) : (
            <>
              <p style={{ fontSize: '1.2rem' }}>Arraste o arquivo .EDF aqui</p>
              <p>ou clique para selecionar</p>
            </>
          )}
        </div>

        {error && <div className="alert alert-error" style={{ marginTop: 12 }}>{error}</div>}

        <div style={{ marginTop: 16 }}>
          <button
            className="btn"
            onClick={handleUpload}
            disabled={uploading || !file || !patientName}
          >
            {uploading ? (
              <><span className="spinner-inline" /> Enviando arquivo...</>
            ) : '🚀 Enviar Exame'}
          </button>
        </div>
      </div>

      {/* STEP 2: Resultado do upload */}
      {examResult && (
        <div className="card">
          <h2>✅ Exame Enviado</h2>
          <div className="alert alert-success">
            Arquivo <b>{examResult.file_name}</b> enviado com sucesso!
          </div>
          <button
            className="btn"
            onClick={handleAnalyze}
            disabled={analyzing || analysisResult}
          >
            {analyzing ? (
              <><span className="spinner-inline" /> Analisando com IA...</>
            ) : analysisResult ? '✅ Análise Concluída' : '🧠 Analisar com IA'}
          </button>
        </div>
      )}

      {/* STEP 3: Resultado da análise */}
      {analysisResult && (
        <div className="card">
          <h2>🔬 Resultado da Análise</h2>
          <div className="metadata">
            <div className="metadata-item">
              <div className="label">Classificação</div>
              <div className="value">{analysisResult.classification?.toUpperCase()}</div>
            </div>
            <div className="metadata-item">
              <div className="label">Ritmo de Base</div>
              <div className="value">{analysisResult.base_rhythm_hz?.toFixed(1) || '-'} Hz</div>
            </div>
            <div className="metadata-item">
              <div className="label">Assimetria</div>
              <div className="value">{analysisResult.has_asymmetry ? 'Sim' : 'Não'}</div>
            </div>
            <div className="metadata-item">
              <div className="label">Spikes detectados</div>
              <div className="value">{analysisResult.spike_count || 0}</div>
            </div>
          </div>
          <div style={{ marginTop: 16 }}>
            <button
              className="btn btn-success"
              onClick={handleGenerateReport}
              disabled={generating || report}
            >
              {generating ? (
                <><span className="spinner-inline" /> Gerando laudo...</>
              ) : report ? '✅ Laudo Gerado' : '📝 Gerar Laudo'}
            </button>
          </div>
        </div>
      )}

      {/* STEP 4: Laudo gerado */}
      {report && (
        <div className="card">
          <h2>📋 Laudo Gerado</h2>
          <span className={`status-badge status-${report.status}`}>
            {report.status?.toUpperCase()}
          </span>
          <div className="report-text" style={{ marginTop: 12 }}>
            {report.generated_text || report.final_text}
          </div>
          <div className="disclaimer">
            {report.disclaimer}
          </div>
          <p style={{ marginTop: 8, fontSize: '0.8rem', color: '#999' }}>
            Gerado por: {report.llm_provider} / {report.llm_model}
          </p>
          <div className="report-actions">
            <button className="btn" onClick={() => navigate(`/report/${examResult.exam_id}`)}>
              📋 Ver / Editar Laudo Completo
            </button>
            <button className="btn btn-success" onClick={handleNewConsult}>
              ➕ Nova Consulta
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
