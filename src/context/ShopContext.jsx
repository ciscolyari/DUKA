import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useAuth } from './AuthContext';
import { shopService } from '../services/shopService';
import { errMsg } from '../utils/format';
const Ctx = createContext(null);
export const useShop = () => useContext(Ctx);
// Admin can own many shops. The selected shop id is sent as X-Shop-ID on every request (see services/api.js).
// Employees belong to exactly one shop, decided by the backend from their token.
export function ShopProvider({ children }) {
  const { user } = useAuth(); const admin = user?.role === 'admin';
  const [shops, setShops] = useState([]), [shopId, setId] = useState(() => localStorage.getItem('duka_shop')), [loaded, setLoaded] = useState(false), [error, setError] = useState('');
  const load = useCallback(async () => {
    if (!admin) { setShops([]); setLoaded(true); return; }
    try {
      const r = await shopService.list(); const list = r.items || r; setShops(list);
      setId((cur) => { const ok = list.find((s) => String(s.id) === String(cur)); const id = ok ? String(cur) : list[0] ? String(list[0].id) : null; id ? localStorage.setItem('duka_shop', id) : localStorage.removeItem('duka_shop'); return id; });
    } catch (e) { setError(errMsg(e)); } finally { setLoaded(true); }
  }, [admin]);
  useEffect(() => { setLoaded(false); load(); }, [load, user]);
  const select = (id) => { localStorage.setItem('duka_shop', String(id)); setId(String(id)); };
  const shop = shops.find((s) => String(s.id) === String(shopId)) || null;
  return <Ctx.Provider value={{ shops, shop, select, reload: load, loaded, error }}>{children}</Ctx.Provider>;
}
