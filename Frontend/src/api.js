import axios from 'axios'
import { CHAT_URL, sessionUrl } from './endpoints'

export async function postChat(sessionId, question) {
  const { data } = await axios.post(CHAT_URL, { session_id: sessionId, question })
  return data
}

export async function getSession(sessionId) {
  const { data } = await axios.get(sessionUrl(sessionId))
  return data
}

export async function deleteSession(sessionId) {
  await axios.delete(sessionUrl(sessionId)).catch(() => {})
}
