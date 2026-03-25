import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/chat': 'https://generative-bi-chatbot.onrender.com',
      '/sessions': 'https://generative-bi-chatbot.onrender.com',
      '/schema': 'https://generative-bi-chatbot.onrender.com',
      '/outputs': 'https://generative-bi-chatbot.onrender.com',
      '/health': 'https://generative-bi-chatbot.onrender.com',
    }
  }
})