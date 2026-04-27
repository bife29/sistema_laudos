import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'

export default function ReportPage() {
  const { examId } = useParams()
  const navigate = useNavigate()
  const [exam, setExam] = useState(null)
  const [report, setReport] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [editing, setEditing] = useState(false)
  const [editText, setEditText] = useState('')
  const [generating, setGenerating] = useState(false)
  const printRef = useRef()

  useEffect(() => {
    loadReport()
  }, [examId])

  const loadReport = async () => {
    setLoading(true)
    setError('')
    try {
      const examRes = await api.get(`/exams/${examId}`)
      setExam(examRes.data)

      try {
        const reportRes = await api.get(`/exams/${examId}/report`)
        setReport(reportRes.data)
        setEditText(reportRes.data.final_text || reportRes.data.generated_text || '')
      } catch {
        setReport(null)
      }

      try {
        const analysisRes = await api.post(`/exams/${examId}/analyze`, null, {
          validateStatus: (s) => s < 500,
        })
        if (analysisRes.status === 200) setAnalysis(analysisRes.data)
      } catch {
        // analysis may not exist yet
      }
    } catch (err) {
      setError('Não foi possível carregar o exame. Verifique se ele existe.')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateReport = async () => {
    setGenerating(true)
    setError('')
    try {
      const res = await api.post(`/exams/${examId}/generate-report`)
      setReport(res.data)
      setEditText(res.data.final_text || res.data.generated_text || '')
      setSuccess('Laudo gerado com sucesso!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Não foi possível gerar o laudo. Verifique se a análise foi executada.')
    } finally {
      setGenerating(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setError('')
    try {
      const res = await api.put(`/exams/${examId}/report`, { final_text: editText })
      setReport(res.data)
      setEditing(false)
      setSuccess('Laudo salvo com sucesso!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Não foi possível salvar as alterações.')
    } finally {
      setSaving(false)
    }
  }

  const handleApprove = async () => {
    setError('')
    try {
      const res = await api.post(`/exams/${examId}/report/approve`)
      setReport(res.data)
      setSuccess('Laudo aprovado com sucesso!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Não foi possível aprovar o laudo.')
    }
  }

  const handleExportPDF = () => {
    const printContent = printRef.current
    if (!printContent) return

    const win = window.open('', '_blank')
    win.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Laudo EEG - ${exam?.file_name || 'Exame'}</title>
        <style>
          * { margin: 0; padding: 0; box-sizing: border-box; }
          body { font-family: 'Times New Roman', Georgia, serif; padding: 40px; color: #222; line-height: 1.6; }
          .pdf-header { text-align: center; border-bottom: 2px solid #1a237e; padding-bottom: 16px; margin-bottom: 24px; }
          .pdf-header h1 { font-size: 20px; color: #1a237e; margin-bottom: 4px; }
          .pdf-header p { font-size: 12px; color: #666; }
          .pdf-section { margin-bottom: 20px; }
          .pdf-section h3 { font-size: 14px; color: #1a237e; border-bottom: 1px solid #ddd; padding-bottom: 4px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
          .pdf-meta { display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 20px; }
          .pdf-meta-item { font-size: 13px; }
          .pdf-meta-item strong { color: #333; }
          .pdf-body { font-size: 14px; white-space: pre-wrap; }
          .pdf-disclaimer { margin-top: 24px; padding: 12px; border: 1px solid #e65100; background: #fff8f0; font-size: 11px; color: #e65100; }
          .pdf-footer { margin-top: 40px; text-align: center; font-size: 11px; color: #999; border-top: 1px solid #ddd; padding-top: 12px; }
          .pdf-signature { margin-top: 60px; text-align: center; }
          .pdf-signature .line { border-top: 1px solid #333; width: 300px; margin: 0 auto 4px; }
          .pdf-signature p { font-size: 13px; }
          @media print { body { padding: 20px; } }
        </style>
      </head>
      <body>
        <div class="pdf-header">
          <h1>LAUDO DE ELETROENCEFALOGRAMA</h1>
          <p>Sistema de Laudos EEG com IA</p>
        </div>
        <div class="pdf-section">
          <h3>Dados do Exame</h3>
          <div class="pdf-meta">
            <div class="pdf-meta-item"><strong>Arquivo:</strong> ${exam?.file_name || '-'}</div>
            <div class="pdf-meta-item"><strong>Canais:</strong> ${exam?.n_channels || '-'}</div>
            <div class="pdf-meta-item"><strong>Duração:</strong> ${exam?.duration_seconds ? (exam.duration_seconds / 60).toFixed(1) + ' min' : '-'}</div>
            <div class="pdf-meta-item"><strong>Indicação:</strong> ${exam?.indication || 'Não informada'}</div>
            <div class="pdf-meta-item"><strong>Data:</strong> ${exam?.created_at ? new Date(exam.created_at).toLocaleDateString('pt-BR') : '-'}</div>
            <div class="pdf-meta-item"><strong>Status:</strong> ${report?.status?.toUpperCase() || '-'}</div>
          </div>
        </div>
        <div class="pdf-section">
          <h3>Laudo</h3>
          <div class="pdf-body">${(report?.final_text || report?.generated_text || '').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div>
        </div>
        ${report?.disclaimer ? `<div class="pdf-disclaimer">${report.disclaimer}</div>` : ''}
        <div class="pdf-signature">
          <div class="line"></div>
          <p>Médico Responsável</p>
          <p style="font-size: 11px; color: #666;">CRM: ____________</p>
        </div>
        <div class="pdf-footer">
          Gerado em ${new Date().toLocaleDateString('pt-BR')} às ${new Date().toLocaleTimeString('pt-BR')} | 
          Provedor: ${report?.llm_provider || '-'} / ${report?.llm_model || '-'}
        </div>
      </body>
      </html>
    `)
    win.document.close()
    setTimeout(() => { win.print() }, 500)
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
          <p>Carregando laudo...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <button className="btn-link" onClick={() => navigate('/')} style={{ marginBottom: 16 }}>
        ← Voltar ao painel
      </button>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* Exam Info */}
      <div className="card">
        <div className="card-header">
          <h2>📄 {exam?.file_name || 'Exame'}</h2>
          <span className={`status-badge status-${exam?.status}`}>
            {exam?.status?.toUpperCase()}
          </span>
        </div>
        <div className="metadata">
          <div className="metadata-item">
            <div className="label">Canais</div>
            <div className="value">{exam?.n_channels || '-'}</div>
          </div>
          <div className="metadata-item">
            <div className="label">Duração</div>
            <div className="value">{exam?.duration_seconds ? `${(exam.duration_seconds / 60).toFixed(1)} min` : '-'}</div>
          </div>
          <div className="metadata-item">
            <div className="label">Taxa</div>
            <div className="value">{exam?.sampling_rate ? `${exam.sampling_rate} Hz` : '-'}</div>
          </div>
          <div className="metadata-item">
            <div className="label">Data</div>
            <div className="value">{formatDate(exam?.created_at)}</div>
          </div>
        </div>
      </div>

      {/* Report */}
      {!report ? (
        <div className="card" style={{ textAlign: 'center', padding: 40 }}>
          <p style={{ color: '#666', marginBottom: 16 }}>Nenhum laudo gerado para este exame.</p>
          <button
            className="btn btn-success"
            onClick={handleGenerateReport}
            disabled={generating}
          >
            {generating ? (
              <><span className="spinner-inline" /> Gerando laudo...</>
            ) : '📝 Gerar Laudo'}
          </button>
        </div>
      ) : (
        <div className="card" ref={printRef}>
          <div className="card-header">
            <h2>📋 Laudo</h2>
            <div className="card-header-actions">
              <span className={`status-badge status-${report.status === 'approved' ? 'analyzed' : 'uploaded'}`}>
                {report.status === 'draft' ? '📝 Rascunho' : report.status === 'review' ? '🔍 Em Revisão' : '✅ Aprovado'}
              </span>
            </div>
          </div>

          {editing ? (
            <>
              <textarea
                className="report-editor"
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                rows={20}
              />
              <div className="report-actions">
                <button className="btn btn-success" onClick={handleSave} disabled={saving}>
                  {saving ? <><span className="spinner-inline" /> Salvando...</> : '💾 Salvar'}
                </button>
                <button className="btn btn-secondary" onClick={() => { setEditing(false); setEditText(report.final_text || report.generated_text || '') }}>
                  Cancelar
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="report-text">
                {report.final_text || report.generated_text}
              </div>

              {report.disclaimer && (
                <div className="disclaimer">{report.disclaimer}</div>
              )}

              <p style={{ marginTop: 8, fontSize: '0.8rem', color: '#999' }}>
                Gerado por: {report.llm_provider} / {report.llm_model} em {formatDate(report.created_at)}
              </p>

              <div className="report-actions">
                {report.status !== 'approved' && (
                  <>
                    <button className="btn" onClick={() => setEditing(true)}>
                      ✏️ Editar Laudo
                    </button>
                    <button className="btn btn-success" onClick={handleApprove}>
                      ✅ Aprovar Laudo
                    </button>
                  </>
                )}
                <button className="btn btn-secondary" onClick={handleExportPDF}>
                  📄 Exportar PDF
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}
