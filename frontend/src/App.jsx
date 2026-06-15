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

async function fetchStates() {
  const res = await fetch(`${API_BASE}/api/states`)
  if (!res.ok) throw new Error('Could not load states')
  return res.json()
}

async function fetchDistrictsForState(state) {
  const params = new URLSearchParams({ state, page_size: '200' })
  const res = await fetch(`${API_BASE}/api/districts?${params}`)
  if (!res.ok) throw new Error('Could not load districts')
  const data = await res.json()
  return data.items
}

export default function App() {
  const [status, setStatus] = useState('loading')
  const [brief, setBrief] = useState(null)
  const [error, setError] = useState('')
  const [states, setStates] = useState([])
  const [districts, setDistricts] = useState([])
  const [selectedState, setSelectedState] = useState('')
  const [selectedDistrictId, setSelectedDistrictId] = useState('')
  const [districtsLoading, setDistrictsLoading] = useState(false)
  const hasSpoken = useRef(false)
  const { supported, isSpeaking, speak, stop } = useReadAloud()

  const applyForecast = useCallback((data) => {
    setBrief(data)
    setStatus('ready')
    if (data.state) setSelectedState(data.state)
    if (data.district_id) setSelectedDistrictId(data.district_id)
  }, [])

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
      applyForecast(data)
    } catch (e) {
      setError(e.message || 'Something went wrong')
      setStatus('error')
    }
  }, [stop, applyForecast])

  const loadForecastForDistrict = useCallback(async (district) => {
    setStatus('loading')
    setError('')
    hasSpoken.current = false
    stop()

    try {
      const data = await fetchForecast(district.latitude, district.longitude)
      applyForecast(data)
    } catch (e) {
      setError(e.message || 'Something went wrong')
      setStatus('error')
    }
  }, [stop, applyForecast])

  useEffect(() => {
    loadForecast()
  }, [loadForecast])

  useEffect(() => {
    fetchStates()
      .then(setStates)
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (!selectedState) {
      setDistricts([])
      return
    }

    let cancelled = false
    setDistrictsLoading(true)
    fetchDistrictsForState(selectedState)
      .then((items) => {
        if (!cancelled) setDistricts(items)
      })
      .catch(() => {
        if (!cancelled) setDistricts([])
      })
      .finally(() => {
        if (!cancelled) setDistrictsLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [selectedState])

  useEffect(() => {
    const onVisible = () => {
      if (document.visibilityState === 'visible') loadForecast()
    }
    document.addEventListener('visibilitychange', onVisible)
    return () => document.removeEventListener('visibilitychange', onVisible)
  }, [loadForecast])

  const handleStateChange = (e) => {
    const state = e.target.value
    setSelectedState(state)
    setSelectedDistrictId('')
  }

  const handleDistrictChange = (e) => {
    const districtId = e.target.value
    setSelectedDistrictId(districtId)
    const district = districts.find((d) => d.id === districtId)
    if (district) loadForecastForDistrict(district)
  }

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
      <div className="center-block">
        <div className="location-picker">
          <p className="location-picker-title">Select location</p>
          <label className="field-label" htmlFor="state-select">
            State
          </label>
          <select
            id="state-select"
            className="location-select"
            value={selectedState}
            onChange={handleStateChange}
          >
            <option value="">Select state</option>
            {states.map((state) => (
              <option key={state} value={state}>
                {state}
              </option>
            ))}
          </select>
          <label className="field-label" htmlFor="district-select">
            District
          </label>
          <select
            id="district-select"
            className="location-select"
            value={selectedDistrictId}
            onChange={handleDistrictChange}
            disabled={!selectedState || districtsLoading}
          >
            <option value="">
              {districtsLoading ? 'Loading districts…' : 'Select district'}
            </option>
            {districts.map((district) => (
              <option key={district.id} value={district.id}>
                {district.name}
              </option>
            ))}
          </select>
          <button type="button" className="detect-btn" onClick={loadForecast}>
            Detect my location
          </button>
        </div>

        {status === 'loading' && (
          <div className="status-block">
            <div className="pulse-icon" aria-hidden="true">🌾</div>
            <p className="status-text">आपका स्थान और मौसम खोज रहे हैं…</p>
          </div>
        )}

        {status === 'error' && (
          <div className="status-block">
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
      </div>
    </main>
  )
}
