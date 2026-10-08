import { t } from '../utils/i18n';
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { authService } from '../services/authService';
import { errMsg } from '../utils/format';

export default function Settings({ admin }) {
  const { user } = useAuth(); const toast = useToast();
  const [f, setF] = useState({ current_password: '', new_password: '', confirm: '' }), [busy, setBusy] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const submit = async (e) => { e.preventDefault();
    if (f.new_password !== f.confirm) return toast(t('New passwords do not match'), 'err');
    setBusy(true);
    try { await authService.changePassword({ current_password: f.current_password, new_password: f.new_password }); toast(t('Password changed')); setF({ current_password: '', new_password: '', confirm: '' }); }
    catch (er) { toast(errMsg(er), 'err'); } finally { setBusy(false); } };
  return (<div><div className="pagehead"><h1>{t('Settings')}</h1></div>
    <div className="grid2">
      <div className="card"><h3>{admin ? t('Admin profile') : t('Profile')}</h3><dl className="dl"><div><dt>{t('Name')}</dt><dd>{user.full_name}</dd></div><div><dt>{t('Role')}</dt><dd>{user.role}</dd></div>{admin && <div><dt>{t('Shop')}</dt><dd>{user.shop_name}</dd></div>}</dl></div>
      {admin ? <form className="card form" onSubmit={submit}><h3>{t('Change password')}</h3>
        <label>{t('Current password')}<input type="password" required value={f.current_password} onChange={set('current_password')} /></label>
        <label>{t('New password')}<input type="password" required minLength={6} value={f.new_password} onChange={set('new_password')} /></label>
        <label>{t('Confirm new password')}<input type="password" required value={f.confirm} onChange={set('confirm')} /></label>
        <button className="btn primary" disabled={busy}>{busy ? t('Saving…') : t('Change password')}</button></form> : <div className="card"><h3>{t('Password')}</h3><p className="muted">{t('Employee passwords can only be changed by your administrator. If you forgot yours or need a new one, ask your administrator.')}</p></div>}
    </div></div>);
}
