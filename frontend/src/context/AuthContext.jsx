import { createContext, useContext, useState, useCallback } from 'react';
import { authService } from '../services/authService';
const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);
export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => { try { return JSON.parse(localStorage.getItem('duka_user')); } catch { return null; } });
  const login = useCallback(async (username, password) => {
    const res = await authService.login(username, password);
    localStorage.setItem('duka_token', res.access_token);
    localStorage.setItem('duka_user', JSON.stringify(res.user));
    setUser(res.user);
    return res.user;
  }, []);
  const logout = useCallback(() => { localStorage.removeItem('duka_token'); localStorage.removeItem('duka_user'); localStorage.removeItem('duka_shop'); setUser(null); }, []);
  return <Ctx.Provider value={{ user, login, logout }}>{children}</Ctx.Provider>;
}
