import axios from 'axios';

// All API requests go to the Django backend (port 8000 by default).
// The Vite dev server proxies /api/* → http://localhost:8000 to avoid CORS.
const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 180_000, // 3 min — AI pipeline can take ~60-90 s
});

export default api;
