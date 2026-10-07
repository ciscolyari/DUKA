import { t } from '../utils/i18n';
import { useState } from 'react';
import { salesService } from '../services/salesService';
import { productService } from '../services/productService';
import { useFetch } from '../hooks/useFetch';
import { useToast } from '../context/ToastContext';
import { State, Empty } from '../components/ui';
import SalesPdfButton from '../components/SalesPdfButton';
import { money, timeOf, errMsg } from '../utils/format';

export function NewSale() {
  const toast = useToast();
  const { data, loading, error, reload } = useFetch(() => productService.list(), []);
  const [pid, setPid] = useState(''), [qty, setQty] = useState(1), [note, setNote] = useState(''), [lines, setLines] = useState([]), [busy, setBusy] = useState(false), [msg, setMsg] = useState(null);
  const products = data?.items || data || [];
  const p = products.find((x) => String(x.id) === String(pid));
  const used = (id) => lines.filter((l) => String(l.pid) === String(id)).reduce((a, l) => a + l.qty, 0);
  const check = () => {
    if (!p) return 'Select a product first.';
    if (qty < 1) return 'Quantity must be at least 1.';
    if (used(p.id) + qty > p.stock) return t('Sale failed. Available stock: {a}. Requested quantity: {q}.', { a: p.stock - used(p.id), q: qty });
    return null;
  };
  const add = () => { const bad = check(); setMsg(bad ? { err: bad } : null); if (bad) return; setLines([...lines, { pid: p.id, name: p.name, price: p.price, qty, note: note.trim() }]); setPid(''); setQty(1); setNote(''); };
  const total = lines.reduce((a, l) => a + l.price * l.qty, 0);
  const submit = async () => {
    let todo = lines;
    if (p) { const bad = check(); if (bad) return setMsg({ err: bad }); todo = [...lines, { pid: p.id, name: p.name, price: p.price, qty, note: note.trim() }]; }
    if (!todo.length) return setMsg({ err: t('Add at least one product to the list.') });
    setBusy(true); setMsg(null);
    const failed = []; let ok = 0, sum = 0;
    for (const l of todo) {
      try { const s = await salesService.create({ product_id: l.pid, quantity: l.qty, note: l.note || undefined }); ok++; sum += Number(s.total ?? l.price * l.qty); }
      catch (er) { failed.push({ ...l, err: errMsg(er) }); }
    }
    setLines(failed); setPid(''); setQty(1); setNote(''); setBusy(false); reload();
    if (ok) toast(`${ok} sale(s) submitted`);
    setMsg({ ok: ok ? `${ok} sale(s) submitted: ${money(sum)}. They are now locked.` : null, err: failed.length ? `${failed.length} failed, kept in the list: ` + failed.map((f) => `${f.name} (${f.err})`).join(' | ') : null });
  };
  return (<div><div className="pagehead"><h1>{t('New Sale')}</h1></div>
    <State loading={loading} error={error} retry={reload}>
      <div style={{ maxWidth: 640, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div className="card form">
          <label>{t('Product')}<select value={pid} onChange={(e) => { setPid(e.target.value); setMsg(null); }}><option value="">{t('Select product…')}</option>{products.map((x) => <option key={x.id} value={x.id} disabled={x.stock <= 0}>{x.name}{x.stock <= 0 ? ' (out of stock)' : ''}</option>)}</select></label>
          <div className="kv"><span>{t('Available stock')}</span><b>{p ? p.stock - used(p.id) : '-'}</b></div>
          <label>{t('Quantity')}<input type="number" min="1" value={qty} onChange={(e) => setQty(Number(e.target.value))} /></label>
          <label>{t('Short note (optional)')}<input maxLength={120} placeholder="e.g. customer on credit, discount given" value={note} onChange={(e) => setNote(e.target.value)} /></label>
          <div className="kv"><span>{t('Unit price')}</span><b>{p ? money(p.price) : '-'}</b></div>
          <div className="kv"><span>{t('Amount')}</span><b>{p ? money(p.price * qty) : '-'}</b></div>
          <button type="button" className="btn" onClick={add}>{t('+ Add to today\'s list')}</button>
        </div>
        <div className="card">
          <h3>{t('Sales to submit')}</h3>
          {lines.length === 0 ? <Empty text={t('Add products one by one, then submit them together.')} /> :
            <div className="tablewrap"><table><thead><tr><th>{t('Product')}</th><th>{t('Qty')}</th><th>{t('Amount')}</th><th>{t('Note')}</th><th /></tr></thead>
              <tbody>{lines.map((l, i) => <tr key={i}><td>{l.name}</td><td>{l.qty}</td><td>{money(l.price * l.qty)}</td><td>{l.note || '-'}</td><td><button className="btn sm danger" onClick={() => setLines(lines.filter((_, j) => j !== i))}>{t('Remove')}</button></td></tr>)}</tbody>
              <tfoot><tr><td colSpan="2">{t('Total')}</td><td colSpan="3">{money(total)}</td></tr></tfoot></table></div>}
          {msg?.err && <div className="errbox" style={{ marginTop: '.8rem' }}>{msg.err}</div>}{msg?.ok && <div className="okbox" style={{ marginTop: '.8rem' }}>{msg.ok}</div>}
          <button className="btn primary lg" style={{ marginTop: '.8rem' }} disabled={busy} onClick={submit}>{busy ? t('Submitting…') : t('Submit sales')}</button>
          <p className="muted">{t('Submitted sales are locked and cannot be edited or deleted.')}</p>
        </div>
      </div></State></div>);
}

export function MySales() {
  const { data, loading, error, reload } = useFetch(() => salesService.mine(), []);
  const rows = data?.items || data || [];
  const total = rows.reduce((a, r) => a + Number(r.total), 0);
  return (<div><div className="pagehead"><h1>{t('My Sales')}</h1></div><SalesPdfButton />
    <State loading={loading} error={error} retry={reload}>
      {rows.length === 0 ? <Empty text={t('You have not made any sales today.')} /> :
        <div className="tablewrap"><table><thead><tr><th>{t('Time')}</th><th>{t('Product')}</th><th>{t('Quantity')}</th><th>{t('Amount')}</th><th>{t('Note')}</th></tr></thead>
          <tbody>{rows.map((r) => <tr key={r.id}><td>🔒 {timeOf(r.created_at)}</td><td>{r.product_name}</td><td>{r.quantity}</td><td>{money(r.total)}</td><td>{r.note || '-'}</td></tr>)}</tbody>
          <tfoot><tr><td colSpan="3">{t('Today\'s Total')}</td><td>{money(total)}</td><td /></tr></tfoot></table></div>}
    </State></div>);
}
