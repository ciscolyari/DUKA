import { t } from '../utils/i18n';
import { useMemo, useState } from 'react';
import { useFetch } from '../hooks/useFetch';
import { useToast } from '../context/ToastContext';
import { Modal, Confirm, State, Empty } from './ui';
import { errMsg } from '../utils/format';

/* Generic table page: search, filters, add/edit/view/delete modals.
   columns: [{key,label,render?}]   fields: [{name,label,type,options,required,createOnly}]
   filters: [{name,label,options:[{value,label}]}] or [{name,label,type:'date'}] */
export default function DataPage({ title, service, listFn, columns, fields = [], filters = [], canAdd, canEdit, canDelete, canView, extraActions, summary, searchKeys = [], onChange, defaults = {}, validate }) {
  const toast = useToast();
  const [q, setQ] = useState(''), [fv, setFv] = useState({}), [form, setForm] = useState(null), [view, setView] = useState(null), [del, setDel] = useState(null), [busy, setBusy] = useState(false);
  const { data, loading, error, reload } = useFetch(() => (listFn || service.list)(fv), [JSON.stringify(fv)]);
  const rows = useMemo(() => (data?.items || data || []).filter((r) => !q || searchKeys.some((k) => String(r[k] ?? '').toLowerCase().includes(q.toLowerCase()))), [data, q]);
  const set = (name, v) => setForm((f) => ({ ...f, values: { ...f.values, [name]: v } }));
  const save = async (e) => {
    e.preventDefault();
    const bad = validate?.(form.values, data?.items || data || [], form.id); if (bad) return toast(bad, 'err');
    setBusy(true);
    try {
      form.id ? await service.update(form.id, form.values) : await service.create(form.values);
      toast(form.id ? t('Changes saved') : t('Created successfully')); setForm(null); reload(); onChange?.();
    } catch (er) { toast(errMsg(er), 'err'); } finally { setBusy(false); }
  };
  const remove = async () => {
    setBusy(true);
    try { await service.remove(del.id); toast(t('Deleted')); setDel(null); reload(); onChange?.(); } catch (er) { toast(errMsg(er), 'err'); } finally { setBusy(false); }
  };
  const hasActions = canEdit || canDelete || canView || extraActions;
  return (<div>
    <div className="pagehead"><h1>{title}</h1>{canAdd && <button className="btn primary" onClick={() => setForm({ values: { ...defaults } })}>{t('+ Add')}</button>}</div>
    {summary && summary(rows)}
    <div className="toolbar">
      {searchKeys.length > 0 && <input placeholder={t('Search…')} value={q} onChange={(e) => setQ(e.target.value)} />}
      {filters.map((f) => f.options
        ? <select key={f.name} value={fv[f.name] || ''} onChange={(e) => setFv({ ...fv, [f.name]: e.target.value })}><option value="">{f.label}: {t('all')}</option>{f.options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}</select>
        : <input key={f.name} type={f.type || 'text'} title={f.label} placeholder={f.label} value={fv[f.name] || ''} onChange={(e) => setFv({ ...fv, [f.name]: e.target.value })} />)}
    </div>
    <State loading={loading} error={error} retry={reload}>
      {rows.length === 0 ? <Empty text={t('No records found.')} /> :
        <div className="tablewrap"><table><thead><tr>{columns.map((c) => <th key={c.key}>{c.label}</th>)}{hasActions && <th>{t('Actions')}</th>}</tr></thead>
          <tbody>{rows.map((r) => <tr key={r.id}>{columns.map((c) => <td key={c.key}>{c.render ? c.render(r) : r[c.key] ?? '-'}</td>)}
            {hasActions && <td className="acts">
              {canView && <button className="btn sm" onClick={() => setView(r)}>{t('View')}</button>}
              {canEdit && <button className="btn sm" onClick={() => setForm({ id: r.id, values: { ...r } })}>{t('Edit')}</button>}
              {extraActions?.(r, reload)}
              {canDelete && <button className="btn sm danger" onClick={() => setDel(r)}>{t('Delete')}</button>}</td>}</tr>)}</tbody></table></div>}
    </State>
    {form && <Modal title={`${form.id ? t('Edit') : t('Add')} ${title}`} onClose={() => setForm(null)}>
      <form onSubmit={save} className="form">{fields.filter((f) => !(form.id && f.createOnly)).map((f) => <label key={f.name}>{f.label}
        {f.type === 'select' ? <select required={f.required} value={form.values[f.name] ?? ''} onChange={(e) => set(f.name, e.target.value)}><option value="">{t('Select…')}</option>{f.options.map((o) => <option key={o.value ?? o} value={o.value ?? o}>{t(o.label ?? o)}</option>)}</select>
          : <input type={f.type || 'text'} required={f.required} min={f.type === 'number' ? 0 : undefined} value={form.values[f.name] ?? ''} onChange={(e) => set(f.name, f.type === 'number' ? Number(e.target.value) : e.target.value)} />}</label>)}
        <div className="row end"><button type="button" className="btn" onClick={() => setForm(null)}>{t('Cancel')}</button><button className="btn primary" disabled={busy}>{busy ? t('Saving…') : t('Save')}</button></div></form></Modal>}
    {view && <Modal title={t('Details')} onClose={() => setView(null)}><dl className="dl">{Object.entries(view).filter(([, v]) => typeof v !== 'object').map(([k, v]) => <div key={k}><dt>{k.replace(/_/g, ' ')}</dt><dd>{String(v)}</dd></div>)}</dl></Modal>}
    {del && <Confirm text={t('This will permanently delete the record. Continue?')} busy={busy} onYes={remove} onNo={() => setDel(null)} />}
  </div>);
}
