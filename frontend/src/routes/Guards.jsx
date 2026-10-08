import { t } from '../utils/i18n';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
export const home = (u) => (u?.role === 'admin' ? '/admin/dashboard' : '/employee/dashboard');
export function RequireRole({ role }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== role) return <Navigate to="/403" replace />;
  return <Outlet />;
}
export const Forbidden = () => {
  const { user } = useAuth();
  return <div className="center"><h1>{t('403 – Access denied')}</h1><p>{t('You do not have permission to view this page.')}</p><a className="btn primary" href={user ? home(user) : '/login'}>{t('Go back')}</a></div>;
};
