import { useCallback, useEffect, useMemo, useState } from 'react'
import { buildReadAloudText, useReadAloud } from './useReadAloud'

const TERMS = [
  { key: 'short_term', label: 'Short term (1–3 days)' },
  { key: 'medium_term', label: 'Medium term (4–7 days)' },
  { key: 'long_term', label: 'Long term (8–16 days)' },
]

const ADVISORY_LABELS = {
  sowing: 'Sowing',
  fertilizer: 'Fertilizer',
  harvest: 'Harvest',
  irrigation: 'Irrigation',
}

const API_BASE = import.meta.env.VITE_API_BASE || ''

async function api(path, options) {
  const res = await fetch(`${API_BASE}${path}`, options)
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(detail || `Request failed (${res.status})`)
  }
  return res.json()
}

function ForecastCard({ item, activeTerm, onShare, onReadAloud, onStopReadAloud, isSpeaking, readAloudSupported }) {
  const forecast = item.forecasts?.[activeTerm]
  if (!forecast) return null

  const termClass =
    activeTerm === 'short_term' ? 'term-short' : activeTerm === 'medium_term' ? 'term-medium' : 'term-long'

  const cardKey = `${item.district_id}-${activeTerm}`
  const speaking = isSpeaking === cardKey

  return (
    <article className="forecast-card">
      <div className="card-header">
        <div>
          <div className="district-name">{item.district_name}</div>
          <div className="meta">{item.state} · {item.language_name}</div>
        </div>
        <span className={`badge ${termClass}`}>{forecast.term_label_local || activeTerm}</span>
      </div>

      <div className="badge-row">
        <span className="badge">Source: {item.source}</span>
        <span className="badge">Updated: {new Date(item.updated_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}</span>
      </div>

      <div className="local-message">{forecast.message_local}</div>
      <div className="english-summary">{forecast.summary_en}</div>

      <div className="advisory-grid">
        {Object.entries(forecast.advisories || {}).map(([key, adv]) => (
          <div key={key} className={`advisory-item ${adv.level}`}>
            <div className="advisory-label">{ADVISORY_LABELS[key] || key}</div>
            <div className="advisory-text">{adv.message_local}</div>
          </div>
        ))}
      </div>

      <div className="card-actions">
        {readAloudSupported && (
          <button
            type="button"
            className={`btn-read-aloud ${speaking ? 'active' : ''}`}
            onClick={() => {
              if (speaking) {
                onStopReadAloud()
              } else {
                onReadAloud(item, activeTerm, cardKey)
              }
            }}
            aria-pressed={speaking}
          >
            {speaking ? 'Stop reading' : 'Read aloud for farmers'}
          </button>
        )}
        <button type="button" className="btn-sms" onClick={() => onShare(item.district_id, activeTerm)}>
          Share with farmer SMS groups
        </button>
      </div>
    </article>
  )
}

function SmsModal({ preview, onClose }) {
  if (!preview) return null

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>SMS blast preview (not sent)</h3>
        <p className="meta">
          {preview.district_name}, {preview.state} · {preview.language} · {preview.character_count} chars
        </p>
        <p className="meta">Source: {preview.source} · Updated {new Date(preview.updated_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}</p>
        <pre>{preview.sms_body}</pre>
        <p><strong>Would send to:</strong></p>
        <ul>
          {preview.farmer_groups.map((g) => (
            <li key={g}>{g}</li>
          ))}
        </ul>
        <p className="meta">{preview.message}</p>
        <div className="modal-actions">
          <button className="btn-secondary" onClick={onClose}>Close</button>
          <button className="btn-primary" onClick={onClose}>Confirm (demo)</button>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const [stats, setStats] = useState(null)
  const [states, setStates] = useState([])
  const [stateFilter, setStateFilter] = useState('')
  const [search, setSearch] = useState('')
  const [activeTerm, setActiveTerm] = useState('short_term')
  const [page, setPage] = useState(1)
  const [forecasts, setForecasts] = useState({ items: [], total: 0 })
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState('')
  const [smsPreview, setSmsPreview] = useState(null)
  const { supported: readAloudSupported, speakingId, speak, stop: stopReadAloud } = useReadAloud()

  const pageSize = 24

  useEffect(() => {
    Promise.all([api('/api/stats'), api('/api/states')])
      .then(([s, st]) => {
        setStats(s)
        setStates(st)
      })
      .catch((e) => setError(e.message))
  }, [])

  const loadForecasts = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
        refresh_missing: 'true',
        term: activeTerm,
      })
      if (stateFilter) params.set('state', stateFilter)

      const data = await api(`/api/forecasts?${params}`)
      let items = data.items

      if (search.trim()) {
        const q = search.trim().toLowerCase()
        items = items.filter(
          (i) => i.district_name.toLowerCase().includes(q) || i.state.toLowerCase().includes(q),
        )
      }

      setForecasts({ items, total: data.total })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [page, pageSize, stateFilter, activeTerm, search])

  useEffect(() => {
    loadForecasts()
  }, [loadForecasts])

  const totalPages = useMemo(() => Math.max(1, Math.ceil((forecasts.total || 0) / pageSize)), [forecasts.total, pageSize])

  const handleRefreshBatch = async () => {
    setRefreshing(true)
    setError('')
    try {
      const params = new URLSearchParams({ limit: '50' })
      if (stateFilter) params.set('state', stateFilter)
      await api(`/api/forecasts/refresh?${params}`, { method: 'POST' })
      await loadForecasts()
    } catch (e) {
      setError(e.message)
    } finally {
      setRefreshing(false)
    }
  }

  const handleShare = async (districtId, term) => {
    try {
      const preview = await api(`/api/sms/preview/${districtId}?term=${term}`, { method: 'POST' })
      setSmsPreview(preview)
    } catch (e) {
      setError(e.message)
    }
  }

  const handleReadAloud = (item, term, cardKey) => {
    const text = buildReadAloudText(item, term)
    speak(cardKey, text, item.language_code)
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <h1>Krishi Mausam AI</h1>
          <p>
            District weather from Open-Meteo, translated into local languages with simple farmer advisories.
            Use Read aloud on any card so farmers can listen in their language. SMS sharing is preview-only for now.
          </p>
        </div>
      </header>

      {stats && (
        <div className="stats-row">
          <span className="stat-pill"><strong>{stats.total_districts}</strong> districts</span>
          <span className="stat-pill"><strong>{stats.total_states}</strong> states/UTs</span>
          <span className="stat-pill"><strong>{stats.languages.length}</strong> local languages</span>
          <span className="stat-pill">Cached: <strong>{stats.cache.cached_districts}</strong></span>
        </div>
      )}

      {error && <div className="error-banner">{error}</div>}

      <div className="toolbar">
        <input
          placeholder="Search district or state..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1) }}
        />
        <select value={stateFilter} onChange={(e) => { setStateFilter(e.target.value); setPage(1) }}>
          <option value="">All states</option>
          {states.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <select value={activeTerm} onChange={(e) => setActiveTerm(e.target.value)}>
          {TERMS.map((t) => (
            <option key={t.key} value={t.key}>{t.label}</option>
          ))}
        </select>
        <button className="btn-secondary" disabled={refreshing} onClick={handleRefreshBatch}>
          {refreshing ? 'Refreshing…' : 'Refresh batch'}
        </button>
        <button className="btn-primary" disabled={loading} onClick={loadForecasts}>
          Reload page
        </button>
      </div>

      <div className="term-tabs">
        {TERMS.map((t) => (
          <button
            key={t.key}
            className={`term-tab ${activeTerm === t.key ? 'active' : ''}`}
            onClick={() => setActiveTerm(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="loading">Loading forecasts for districts… (first load may take a moment)</div>
      ) : forecasts.items.length === 0 ? (
        <div className="empty">No forecasts found. Try another state or click Refresh batch.</div>
      ) : (
        <div className="cards-grid">
          {forecasts.items.map((item) => (
            <ForecastCard
              key={item.district_id}
              item={item}
              activeTerm={activeTerm}
              onShare={handleShare}
              onReadAloud={handleReadAloud}
              onStopReadAloud={stopReadAloud}
              isSpeaking={speakingId}
              readAloudSupported={readAloudSupported}
            />
          ))}
        </div>
      )}

      <div className="pagination">
        <button className="btn-secondary" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Previous</button>
        <span className="meta">Page {page} of {totalPages}</span>
        <button className="btn-secondary" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>Next</button>
      </div>

      <SmsModal preview={smsPreview} onClose={() => setSmsPreview(null)} />
    </div>
  )
}
