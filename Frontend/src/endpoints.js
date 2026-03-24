import { API_BASE } from './constants'

export const CHAT_URL = `${API_BASE}/chat`
export const sessionUrl = (sessionId) => `${API_BASE}/sessions/${sessionId}`
