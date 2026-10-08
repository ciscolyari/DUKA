import { t } from '../utils/i18n';
import { useState } from 'react';
import { NavLink, Navigate, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useShop } from '../context/ShopContext';
import ThemeToggle from '../components/ThemeToggle';
import { Spinner } from '../components/ui';
const ADMIN = [['dashboard','Dashboard','📊'],['shops','Shops','🏬'],['products','Products','📦'],['inventory','Inventory','🗃️'],['sales','Sales','💰'],['employees','Employees','👥'],['expenses','Expenses','🧾'],['reports','Reports','📈'],['subscription','Subscription','⭐'],['billing','Billing History','💳'],['settings','Settings','⚙️']];
const EMP = [['dashboard','Dashboard','📊'],['products','Products','📦'],['sales/new','New Sale','🛒'],['sales','My Sales','💰'],['expenses','My Expenses','🧾'],['inventory','Inventory','🗃️'],['settings','Settings','⚙️']];
export default function AppLayout() {
  const { user, logout } = useAuth(); const { shops, shop, select, loaded } = useShop(); const nav = useNavigate(); const { pathname } = useLocation(); const [open, setOpen] = useState(false);
  const admin = user.role === 'admin'; const base = admin ? '/admin' : '/employee'; const items = admin ? ADMIN : EMP;
  let body = <Outlet key={admin ? shop?.id : 'emp'} />;   // remount pages when the shop changes so no data is mixed
  if (admin && !loaded) body = <Spinner />;
  else if (admin && shops.length === 0 && !pathname.endsWith('/shops')) body = <Navigate to="/admin/shops" replace />;
  return (<div className="shell">
    <aside className={open ? 'side open' : 'side'}>
      <div className="brand">{t('DUKA AI')}<small>{admin ? shop?.name || t('No shop yet') : user.shop_name}</small></div>
      <nav>{items.map(([p, l, i]) => <NavLink key={p} to={`${base}/${p}`} end onClick={() => setOpen(false)}><span>{i}</span>{t(l)}</NavLink>)}
        <button onClick={() => { logout(); nav('/login'); }}><span>🚪</span>{t('Logout')}</button></nav>
    </aside>
    {open && <div className="scrim" onClick={() => setOpen(false)} />}
    <div className="main">
      <header className="top"><button className="burger" onClick={() => setOpen(true)} aria-label={t('Menu')}>☰</button>
        {admin && shops.length > 0 && <select className="shopsel" aria-label={t('Current shop')} value={shop?.id ?? ''} onChange={(e) => select(e.target.value)}>{shops.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}</select>}
        <span>{user.full_name} · {admin ? t('Administrator') : t('Employee')}</span><ThemeToggle /></header>
      <main>{body}</main>
    </div></div>);
}
