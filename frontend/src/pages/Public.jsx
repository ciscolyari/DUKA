import { t } from '../utils/i18n';
import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { authService } from '../services/authService';
import { errMsg } from '../utils/format';
import { home } from '../routes/Guards';
import ThemeToggle from '../components/ThemeToggle';

export function Landing() {
  const feats = [['📦','Products & stock','Know what you have and what is running low.'],['💰','Sales','Employees record sales; every sale locks and cannot be changed.'],['🧾','Matumizi','Track rent, electricity, transport and salaries.'],['📈','Profit','Sales minus expenses, shown every day.'],['⭐','Subscription','Choose a plan and pay from the app.']];
  return (<div className="landing">
    <header className="lhead"><b>{t('DUKA AI')}</b><span><ThemeToggle /> <Link className="btn" to="/login">{t('Login')}</Link> <Link className="btn primary" to="/register">{t('Get Started')}</Link></span></header>
    <section className="hero"><h1>{t('Run your shop without the notebook.')}</h1><p>{t('DUKA AI keeps your sales, stock, expenses and employees in one place, and tells you whether you made a profit today.')}</p>
      <Link className="btn primary lg" to="/register">{t('Get Started')}</Link></section>
    <section className="feats">{feats.map(([i, ti, d]) => <div className="card" key={ti}><div className="ico">{i}</div><h3>{t(ti)}</h3><p>{t(d)}</p></div>)}</section>
    <section className="how"><h2>{t('How DUKA works')}</h2><ol><li>{t('Register your shop and add your products.')}</li><li>{t('Create accounts for your employees.')}</li><li>{t('Employees record sales; stock goes down automatically.')}</li><li>{t('Add your expenses and see your profit.')}</li></ol></section>
  </div>);
}

export function Login() {
  const { login } = useAuth(); const nav = useNavigate(); const toast = useToast();
  const [u, setU] = useState(''), [p, setP] = useState(''), [busy, setBusy] = useState(false);
  const submit = async (e) => { e.preventDefault(); setBusy(true);
    try { const usr = await login(u, p); nav(home(usr)); } catch (er) { toast(errMsg(er), 'err'); } finally { setBusy(false); } };
  return (<div className="authpage"><form className="card authbox" onSubmit={submit}>
    <div className="row end"><ThemeToggle /></div><h1>{t('Login')}</h1>
    <label>{t('Email / username')}<input required value={u} onChange={(e) => setU(e.target.value)} autoComplete="username" /></label>
    <label>{t('Password')}<input required type="password" value={p} onChange={(e) => setP(e.target.value)} autoComplete="current-password" /></label>
    <button className="btn primary" disabled={busy}>{busy ? t('Signing in…') : t('Login')}</button>
    <p className="muted"><Link to="/forgot-password">{t('Forgot password?')}</Link></p>
    <p className="muted">{t('New shop? ')}<Link to="/register">{t('Register as administrator')}</Link>{t('. Employees: use the account your administrator created for you.')}</p>
  </form></div>);
}

export function Register() {
  const nav = useNavigate(); const toast = useToast();
  const [f, setF] = useState({ shop_name: '', full_name: '', username: '', password: '', confirm: '' }), [busy, setBusy] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const submit = async (e) => { e.preventDefault();
    if (f.password !== f.confirm) return toast(t('Passwords do not match'), 'err');
    setBusy(true);
    try { const { confirm, ...body } = f; await authService.registerShop(body); toast(t('Shop registered. Please log in.')); nav('/login'); }
    catch (er) { toast(errMsg(er), 'err'); } finally { setBusy(false); } };
  return (<div className="authpage"><form className="card authbox" onSubmit={submit}>
    <div className="row end"><ThemeToggle /></div><h1>{t('Register your shop')}</h1><p className="muted">{t('The email you register with becomes the administrator account. The administrator then creates employee accounts.')}</p>
    <label>{t('Shop name')}<input required value={f.shop_name} onChange={set('shop_name')} /></label>
    <label>{t('Your full name')}<input required value={f.full_name} onChange={set('full_name')} /></label>
    <label>{t('Admin email')}<input required type="email" value={f.username} onChange={set('username')} /></label>
    <label>{t('Password')}<input required minLength={6} type="password" value={f.password} onChange={set('password')} /></label>
    <label>{t('Confirm password')}<input required type="password" value={f.confirm} onChange={set('confirm')} /></label>
    <button className="btn primary" disabled={busy}>{busy ? t('Creating…') : t('Register')}</button>
    <p className="muted">{t('Already registered? ')}<Link to="/login">{t('Login')}</Link></p>
  </form></div>);
}

export function ForgotPassword() {
  const toast = useToast();
  const [u, setU] = useState(''), [busy, setBusy] = useState(false), [sent, setSent] = useState(null);
  const submit = async (e) => {
    e.preventDefault(); setBusy(true);
    try { setSent((await authService.forgotPassword(u.trim())) || {}); } catch (er) { toast(errMsg(er), 'err'); } finally { setBusy(false); }
  };
  return (<div className="authpage"><div className="card authbox">
    <div className="row end"><ThemeToggle /></div><h1>{t('Forgot password')}</h1>
    {sent ? <>
      <div className="okbox">{t('If this is an administrator account, a password reset link has been sent to its email. Check your inbox and spam folder.')}</div>
      {window.__DUKA_PREVIEW__ && sent.dev_token && <p className="muted">{t('Preview only (no email is sent): ')}<Link to={`/reset-password?token=${sent.dev_token}`}>{t('open the reset link')}</Link></p>}
      <p className="muted">{t('Employee? Employees cannot reset their own password. Ask your administrator to set a new one for you.')}</p>
      <Link className="btn" to="/login">{t('Back to login')}</Link></> :
      <form className="form" onSubmit={submit}>
        <p className="muted">{t('Administrators: enter your registered email and we will send a reset link. Employees: your administrator must reset your password for you.')}</p>
        <label>{t('Email')}<input required value={u} onChange={(e) => setU(e.target.value)} autoComplete="username" /></label>
        <button className="btn primary" disabled={busy}>{busy ? t('Sending…') : t('Send reset link')}</button>
        <Link to="/login">{t('Back to login')}</Link></form>}
  </div></div>);
}

export function ResetPassword() {
  const [sp] = useSearchParams(); const token = sp.get('token'); const nav = useNavigate(); const toast = useToast();
  const [p, setP] = useState(''), [p2, setP2] = useState(''), [busy, setBusy] = useState(false);
  const submit = async (e) => {
    e.preventDefault(); if (p !== p2) return toast(t('Passwords do not match'), 'err');
    setBusy(true);
    try { await authService.resetPassword(token, p); toast(t('Password changed. Please log in.')); nav('/login'); } catch (er) { toast(errMsg(er), 'err'); } finally { setBusy(false); }
  };
  if (!token) return (<div className="authpage"><div className="card authbox"><h1>{t('Reset password')}</h1><div className="errbox">{t('This reset link is invalid. Please request a new one.')}</div><Link className="btn primary" to="/forgot-password">{t('Request new link')}</Link></div></div>);
  return (<div className="authpage"><form className="card authbox" onSubmit={submit}>
    <div className="row end"><ThemeToggle /></div><h1>{t('Set a new password')}</h1>
    <label>{t('New password')}<input required minLength={6} type="password" autoComplete="new-password" value={p} onChange={(e) => setP(e.target.value)} /></label>
    <label>{t('Confirm password')}<input required type="password" autoComplete="new-password" value={p2} onChange={(e) => setP2(e.target.value)} /></label>
    <button className="btn primary" disabled={busy}>{busy ? t('Saving…') : t('Change password')}</button>
  </form></div>);
}
