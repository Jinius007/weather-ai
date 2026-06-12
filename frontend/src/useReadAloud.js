import { useCallback, useEffect, useState } from 'react'

const LANG_VOICE_MAP = {
  hi: 'hi-IN',
  te: 'te-IN',
  ta: 'ta-IN',
  kn: 'kn-IN',
  ml: 'ml-IN',
  mr: 'mr-IN',
  gu: 'gu-IN',
  bn: 'bn-IN',
  pa: 'pa-IN',
  or: 'or-IN',
  as: 'as-IN',
}

function pickVoice(langCode) {
  if (!('speechSynthesis' in window)) return null
  const target = LANG_VOICE_MAP[langCode] || 'hi-IN'
  const voices = window.speechSynthesis.getVoices()
  return (
    voices.find((v) => v.lang === target)
    || voices.find((v) => v.lang.startsWith(target.split('-')[0]))
    || voices.find((v) => v.lang.startsWith('hi'))
    || voices[0]
    || null
  )
}

export function useReadAloud() {
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [supported] = useState(() => typeof window !== 'undefined' && 'speechSynthesis' in window)

  const stop = useCallback(() => {
    if (!supported) return
    window.speechSynthesis.cancel()
    setIsSpeaking(false)
  }, [supported])

  const speak = useCallback(
    (text, langCode) => {
      if (!supported || !text?.trim()) return

      window.speechSynthesis.cancel()

      const utterance = new SpeechSynthesisUtterance(text)
      const voice = pickVoice(langCode)
      if (voice) {
        utterance.voice = voice
        utterance.lang = voice.lang
      } else {
        utterance.lang = LANG_VOICE_MAP[langCode] || 'hi-IN'
      }
      utterance.rate = 0.88
      utterance.pitch = 1

      utterance.onend = () => setIsSpeaking(false)
      utterance.onerror = () => setIsSpeaking(false)

      setIsSpeaking(true)
      window.speechSynthesis.speak(utterance)
    },
    [supported],
  )

  useEffect(() => {
    if (!supported) return undefined
    const loadVoices = () => window.speechSynthesis.getVoices()
    loadVoices()
    window.speechSynthesis.addEventListener('voiceschanged', loadVoices)
    return () => {
      window.speechSynthesis.removeEventListener('voiceschanged', loadVoices)
      window.speechSynthesis.cancel()
    }
  }, [supported])

  return { supported, isSpeaking, speak, stop }
}
