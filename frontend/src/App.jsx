import { useCallback, useEffect, useRef, useState } from 'react'
import { useReadAloud } from './useReadAloud'

const API_BASE = import.meta.env.VITE_API_BASE || ''

function getGpsLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('GPS not available'))
      return
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
      (err) => reject(new Error(err.message || 'Location denied')),
      { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 },
    )
  })
}

async function fetchForecast(lat, lon) {
  const params = new URLSearchParams({ _fresh: String(Date.now()) })
  if (lat != null && lon != null) {
    params.set('lat', String(lat))
    params.set('lon', String(lon))
  }

  const res = await fetch(`${API_BASE}/api/local-forecast?${params}`, {
    cache: 'no-store',
    headers: { 'Cache-Control': 'no-cache', Pragma: 'no-cache' },
  })

  if (!res.ok) {
    let detail = 'Could not load forecast'
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch {
      detail = (await res.text()) || detail
    }
    throw new Error(detail)
  }

  return res.json()
}

export default function App() {
  const [status, setStatus] = useState('loading')
  const [brief, setBrief] = useState(null)
  const [error, setError] = useState('')
  const hasSpoken = useRef(false)
  const { supported, isSpeaking, speak, stop } = useReadAloud()

  const loadForecast = useCallback(async () => {
    setStatus('loading')
    setError('')
    hasSpoken.current = false
    stop()

    try {
      let data
      try {
        const { lat, lon } = await getGpsLocation()
        data = await fetchForecast(lat, lon)
      } catch {
        data = await fetchForecast(null, null)
      }
      setBrief(data)
      setStatus('ready')
    } catch (e) {
      setError(e.message || 'Something went wrong')
      setStatus('error')
    }
  }, [stop])

  useEffect(() => {
    loadForecast()
  }, [loadForecast])

  useEffect(() => {
    const onVisible = () => {
      if (document.visibilityState === 'visible') loadForecast()
    }
    document.addEventListener('visibilitychange', onVisible)
    return () => document.removeEventListener('visibilitychange', onVisible)
  }, [loadForecast])

  useEffect(() => {
    if (status !== 'ready' || !brief?.message_local || hasSpoken.current) return

    const timer = setTimeout(() => {
      if (!supported) return
      hasSpoken.current = true
      speak(brief.message_local, brief.language_code)
    }, 400)

    return () => clearTimeout(timer)
  }, [status, brief, supported, speak])

  return (
    <main className="farmer-screen">
      {status === 'loading' && (
        <div className="center-block">
          <div className="pulse-icon" aria-hidden="true">🌾</div>
          <p className="status-text">आपका स्थान और मौसम खोज रहे हैं…</p>
        </div>
      )}

      {status === 'error' && (
        <div className="center-block">
          <p className="error-text">{error}</p>
          <button type="button" className="retry-btn" onClick={loadForecast}>
            फिर से कोशिश करें
          </button>
        </div>
      )}

      {status === 'ready' && brief && (
        <div className="brief-block">
          <p className="area-label">{brief.district_name}, {brief.state}</p>
          <div className="message-local">{brief.message_local}</div>
          {supported && (
            <button
              type="button"
              className={`listen-btn ${isSpeaking ? 'active' : ''}`}
              onClick={() => (isSpeaking ? stop() : speak(brief.message_local, brief.language_code))}
            >
              {isSpeaking ? '⏹ रोकें' : '🔊 फिर सुनें'}
            </button>
          )}
        </div>
      )}
    </main>
  )
}
