import { createContext, useContext, useState, useCallback } from 'react';
const Ctx = createContext(() => {});
export const useToast = () => useContext(Ctx);
export function ToastProvider({ children }) {
  const [items, setItems] = useState([]);
  const toast = useCallback((msg, type = 'ok') => {
    const id = Date.now() + Math.random();
    setItems((x) => [...x, { id, msg, type }]);
    setTimeout(() => setItems((x) => x.filter((i) => i.id !== id)), 4000);
  }, []);
  return (<Ctx.Provider value={toast}>{children}
    <div className="toasts" role="status">{items.map((t) => <div key={t.id} className={`toast ${t.type}`}>{t.msg}</div>)}</div></Ctx.Provider>);
}
