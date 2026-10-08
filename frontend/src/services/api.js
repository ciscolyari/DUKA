import { t } from '../utils/i18n';
import axios from 'axios';
const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || t('http://localhost:8000/api') });
api.interceptors.request.use((c) => {
  const t = localStorage.getItem('duka_token');
  if (t) c.headers.Authorization = `Bearer ${t}`;
  return c;
});
api.interceptors.response.use((r) => r, (e) => {
  const s = e.response?.status, d = e.response?.data?.detail;
  let msg = t('Something went wrong. Try again.');
  if (!e.response) msg = t('Cannot reach the server. Check your connection.');
  else if (s === 401) {
    localStorage.removeItem('duka_token'); localStorage.removeItem('duka_user');
    if (!location.pathname.startsWith('/login')) location.href = '/login';
    msg = d || t('Session expired. Please log in again.');
  } else if (s === 403) msg = t('Access denied. You do not have permission.');
  else if (s === 404) msg = t('Not found.');
  else if (s === 409) msg = typeof d === 'string' ? d : 'This already exists. Use a different value.';
  else if (s === 422) msg = Array.isArray(d) ? d.map((x) => `${x.loc?.slice(-1)}: ${x.msg}`).join('; ') : d || t('Invalid input.');
  else if (s >= 500) msg = t('Server error. Try again later.');
  else if (typeof d === 'string') msg = d;
  e.userMessage = msg;
  return Promise.reject(e);
});
export const unwrap = (p) => p.then((r) => r.data);
export default api;
