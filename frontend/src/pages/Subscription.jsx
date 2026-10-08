import { t } from '../utils/i18n';
import { useState } from 'react';
import { subscriptionService } from '../services/subscriptionService';
import { useFetch } from '../hooks/useFetch';
import { State, Badge } from '../components/ui';
import { money, dateOf } from '../utils/format';

export default function Subscription() {
  const cur = useFetch(subscriptionService.current), plans = useFetch(subscriptionService.plans);
  const c = cur.data;
  return (<div><div className="pagehead"><h1>{t('Subscription')}</h1></div>
    <State loading={cur.loading} error={cur.error} retry={cur.reload}>{c
      ? <div className="card cur"><h3>{t('Current plan: {plan}', { plan: c.plan_name })}</h3>
        <div className="grid4"><div><small>{t('Status')}</small><br /><Badge kind={c.status === 'active' ? 'green' : 'red'}>{c.status}</Badge></div><div><small>{t('Started')}</small><br />{dateOf(c.start_date)}</div><div><small>{t('Expires')}</small><br />{dateOf(c.expiry_date)}</div><div><small>{t('Remaining')}</small><br />{c.days_left} {t('days')}</div><div><small>{t('Price')}</small><br />{money(c.price)}</div><div><small>{t('Payment')}</small><br />{c.payment_status}</div></div></div>
      : <div className="card"><h3>{t('No current subscription')}</h3><p className="muted">{t('Your shop does not have a current subscription. Review the available plans below.')}</p></div>}</State>
    <h2>{t('Available plans')}</h2>
    <div className="errbox">{t('Plan payments are not available until a payment provider is integrated.')}</div>
    <State loading={plans.loading} error={plans.error} retry={plans.reload}><div className="grid3">{(plans.data || []).map((p) => <div className="card plan" key={p.id}>
      <h3>{p.name}</h3><div className="price">{money(p.price)}<small> / {p.duration_days} days</small></div>
      <ul>{(p.features || []).map((f) => <li key={f}>{f}</li>)}</ul>
      <button className="btn primary" disabled>{c?.plan_name === p.name && c?.status === 'active' ? t('Current plan') : t('Subscribe')}</button></div>)}</div></State>
  </div>);
}
