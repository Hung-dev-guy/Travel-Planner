import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 120_000, // 2 min — pipeline takes ~30–60 s (AI ranking + scheduling)
});

export default api;
