import { useState, useEffect } from 'react';
import { getLang, setLang } from '../i18n';
const initial = () => {
  try { const s = localStorage.getItem('duka_theme'); if (s) return s; } catch { /* ignore */ }
  return matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};
document.documentElement.dataset.theme = initial();
export function LangToggle() {
  const [l, setL] = useState(getLang);
  return <select className="langsel" aria-label="Language" value={l} onChange={(e) => { setLang(e.target.value); setL(e.target.value); }}><option value="en">English</option><option value="sw">Kiswahili</option></select>;
}
export default function ThemeToggle() {
  const [t, setT] = useState(initial);
  useEffect(() => { document.documentElement.dataset.theme = t; try { localStorage.setItem('duka_theme', t); } catch { /* ignore */ } }, [t]);
  return <><LangToggle /><button type="button" className="btn sm" aria-label="Toggle dark mode" onClick={() => setT(t === 'dark' ? 'light' : 'dark')}>{t === 'dark' ? '☀️ Light' : '🌙 Dark'}</button></>;
}
