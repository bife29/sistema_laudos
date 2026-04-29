import { useState, useEffect } from 'react'
import api from '../services/api'

export default function ReferencesPage() {
  const [sources, setSources] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [file, setFile] = useState(null)
  const [sourceName, setSourceName] = useState('')
  const [chapter, setChapter] = useState('')
  const [deletingSource, setDeletingSource] = useState(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [sourcesRes, statsRes] = await Promise.all([
        api.get('/references/sources'),
        api.get('/references/stats'),
      ])
      setSources(sourcesRes.data)
      setStats(statsRes.data)
    } catch (err) {
      setError('Erro ao carregar dados de referências')
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!file || !sourceName.trim()) {
      setError('Selecione um arquivo PDF e informe o nome da fonte')
      return
    }

    setUploading(true)
    setError('')
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('source_name', sourceName.trim())
      if (chapter.trim()) formData.append('chapter', chapter.trim())

      await api.post('/references/upload-pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000,
      })

      setSuccess('PDF processado com sucesso! Chunks de texto e embeddings foram gerados.')
      setFile(null)
      setSourceName('')
      setChapter('')
      setTimeout(() => setSuccess(''), 5000)
      await loadData()
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao processar o PDF')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (name) => {
    if (!window.confirm(`Tem certeza que deseja remover "${name}" e todos os seus chunks?`)) return

    setDeletingSource(name)
    setError('')
    try {
      const res = await api.delete(`/references/sources/${encodeURIComponent(name)}`)
      setSuccess(`Fonte "${name}" removida (${res.data.deleted} chunks excluídos)`)
      setTimeout(() => setSuccess(''), 5000)
      await loadData()
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao remover fonte')
    } finally {
      setDeletingSource(null)
    }
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading-container">
          <div className="spinner" />
          <p>Carregando referências...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <h1 style={{ marginBottom: 8 }}>📚 Referências RAG</h1>
      <p style={{ color: '#666', marginBottom: 24, fontSize: '0.95rem' }}>
        Gerencie livros e documentos médicos usados como base de conhecimento para geração de laudos.
      </p>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* Stats */}
      {stats && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="card-header">
            <h2>📊 Estatísticas RAG</h2>
            <span className={`status-badge ${stats.rag_enabled ? 'status-analyzed' : 'status-error'}`}>
              {stats.rag_enabled ? '✅ Ativo' : '❌ Desativado'}
            </span>
          </div>
          <div className="metadata">
            <div className="metadata-item">
              <div className="label">Fontes</div>
              <div className="value">{stats.total_sources}</div>
            </div>
            <div className="metadata-item">
              <div className="label">Chunks de Texto</div>
              <div className="value">{stats.total_reference_chunks}</div>
            </div>
            <div className="metadata-item">
              <div className="label">Embeddings de Laudos</div>
              <div className="value">{stats.total_report_embeddings}</div>
            </div>
            <div className="metadata-item">
              <div className="label">Provedor</div>
              <div className="value">{stats.embedding_provider || 'N/A'}</div>
            </div>
          </div>
        </div>
      )}

      {/* Upload Form */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h2>📤 Adicionar Referência</h2>
        </div>
        <form onSubmit={handleUpload}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div>
              <label style={{ display: 'block', marginBottom: 4, fontWeight: 600, fontSize: '0.9rem' }}>
                Nome da Fonte *
              </label>
              <input
                type="text"
                className="input"
                placeholder="Ex: Niedermeyer - Electroencephalography"
                value={sourceName}
                onChange={(e) => setSourceName(e.target.value)}
                disabled={uploading}
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: 4, fontWeight: 600, fontSize: '0.9rem' }}>
                Capítulo (opcional)
              </label>
              <input
                type="text"
                className="input"
                placeholder="Ex: Cap. 13 - EEG Normal do Adulto"
                value={chapter}
                onChange={(e) => setChapter(e.target.value)}
                disabled={uploading}
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: 4, fontWeight: 600, fontSize: '0.9rem' }}>
                Arquivo PDF *
              </label>
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setFile(e.target.files[0])}
                disabled={uploading}
              />
            </div>
            <button
              type="submit"
              className="btn btn-success"
              disabled={uploading || !file || !sourceName.trim()}
              style={{ alignSelf: 'flex-start' }}
            >
              {uploading ? (
                <><span className="spinner-inline" /> Processando PDF...</>
              ) : '📤 Enviar e Processar'}
            </button>
          </div>
        </form>
      </div>

      {/* Sources List */}
      <div className="card">
        <div className="card-header">
          <h2>📖 Fontes Cadastradas</h2>
        </div>
        {sources.length === 0 ? (
          <p style={{ color: '#999', padding: 16, textAlign: 'center' }}>
            Nenhuma fonte cadastrada. Faça upload de um PDF acima.
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {sources.map((src) => (
              <div
                key={src.source_name}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px 16px',
                  background: '#f8f9fa',
                  borderRadius: 8,
                  border: '1px solid #e2e8f0',
                }}
              >
                <div>
                  <div style={{ fontWeight: 600 }}>{src.source_name}</div>
                  <div style={{ fontSize: '0.85rem', color: '#666' }}>
                    {src.chunk_count} chunks
                    {src.page_range && ` · Páginas ${src.page_range}`}
                  </div>
                </div>
                <button
                  className="btn btn-danger"
                  onClick={() => handleDelete(src.source_name)}
                  disabled={deletingSource === src.source_name}
                  style={{ fontSize: '0.85rem', padding: '6px 12px' }}
                >
                  {deletingSource === src.source_name ? (
                    <><span className="spinner-sm" /> Removendo...</>
                  ) : '🗑️ Remover'}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
