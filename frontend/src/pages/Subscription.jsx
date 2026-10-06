import { t } from '../utils/i18n';
import { useEffect, useRef, useState } from 'react';
import { subscriptionService } from '../services/subscriptionService';
import { paymentService } from '../services/paymentService';
import { useFetch } from '../hooks/useFetch';
import { State, Badge, Modal } from '../components/ui';
import { money, dateOf, errMsg } from '../utils/format';

function PayFlow({ plan, onClose, onDone }) {
  const [step, setStep] = useState('review'), [method, setMethod] = useState('Mobile money'), [phone, setPhone] = useState(''), [tx, setTx] = useState(null), [err, setErr] = useState('');
  const timer = useRef();
  useEffect(() => () => clearInterval(timer.current), []);
  const start = async () => {
    setStep('processing'); setErr('');
    try {
      const t = await paymentService.initiate({ plan_id: plan.id, method, phone }); setTx(t);
      timer.current = setInterval(async () => {
        try { const s = await paymentService.status(t.transaction_id); setTx(s);
          if (s.status !== 'pending') { clearInterval(timer.current); setStep(s.status === 'paid' ? 'success' : 'failed'); if (s.status === 'paid') onDone(); }
        } catch (e) { clearInterval(timer.current); setErr(errMsg(e)); setStep('failed'); }
      }, 3000);
    } catch (e) { setErr(errMsg(e)); setStep('failed'); }
  };
  return (<Modal title={`${t('Subscribe')}: ${plan.name}`} onClose={onClose}>
    <dl className="dl"><div><dt>{t('Plan')}</dt><dd>{plan.name}</dd></div><div><dt>{t('Price')}</dt><dd>{money(plan.price)}</dd></div><div><dt>{t('Duration')}</dt><dd>{plan.duration_days} days</dd></div>
      {tx && <><div><dt>{t('Payment status')}</dt><dd>{tx.status}</dd></div><div><dt>{t('Transaction ID')}</dt><dd>{tx.transaction_id}</dd></div>{tx.paid_at && <div><dt>{t('Payment date')}</dt><dd>{dateOf(tx.paid_at)}</dd></div>}</>}</dl>
    {step === 'review' && <div className="form"><label>{t('Payment method')}<select value={method} onChange={(e) => setMethod(e.target.value)}><option>{t('Mobile money')}</option><option>{t('Bank')}</option></select></label>
      <label>{t('Phone number')}<input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder={t('07XXXXXXXX')} /></label>
      <div className="row end"><button className="btn" onClick={onClose}>{t('Cancel')}</button><button className="btn primary" onClick={start}>Pay {money(plan.price)}</button></div></div>}
    {step === 'processing' && <div className="center"><div className="spinner" /><p>{t('Waiting for payment confirmation…')}</p></div>}
    {step === 'success' && <div className="okbox">{t('Payment received. Your subscription is active.')}</div>}
    {step === 'failed' && <><div className="errbox">{err || 'Payment failed or was cancelled.'}</div><div className="row end"><button className="btn primary" onClick={() => setStep('review')}>{t('Try again')}</button></div></>}
  </Modal>);
}

export default function Subscription() {
  const cur = useFetch(subscriptionService.current), plans = useFetch(subscriptionService.plans);
  const [sel, setSel] = useState(null); const c = cur.data;
  return (<div><div className="pagehead"><h1>{t('Subscription')}</h1></div>
    <State loading={cur.loading} error={cur.error} retry={cur.reload}>{c && <div className="card cur"><h3>Current plan: {c.plan_name}</h3>
      <div className="grid4"><div><small>{t('Status')}</small><br /><Badge kind={c.status === 'active' ? 'green' : 'red'}>{c.status}</Badge></div><div><small>{t('Started')}</small><br />{dateOf(c.start_date)}</div><div><small>{t('Expires')}</small><br />{dateOf(c.expiry_date)}</div><div><small>{t('Remaining')}</small><br />{c.days_left} days</div><div><small>{t('Price')}</small><br />{money(c.price)}</div><div><small>{t('Payment')}</small><br />{c.payment_status}</div></div></div>}</State>
    <h2>{t('Available plans')}</h2>
    <State loading={plans.loading} error={plans.error} retry={plans.reload}><div className="grid3">{(plans.data || []).map((p) => <div className="card plan" key={p.id}>
      <h3>{p.name}</h3><div className="price">{money(p.price)}<small> / {p.duration_days} days</small></div>
      <ul>{(p.features || []).map((f) => <li key={f}>{f}</li>)}</ul>
      <button className="btn primary" disabled={c?.plan_name === p.name && c?.status === 'active'} onClick={() => setSel(p)}>{c?.plan_name === p.name && c?.status === 'active' ? t('Current plan') : t('Subscribe')}</button></div>)}</div></State>
    {sel && <PayFlow plan={sel} onClose={() => setSel(null)} onDone={cur.reload} />}
  </div>);
}
