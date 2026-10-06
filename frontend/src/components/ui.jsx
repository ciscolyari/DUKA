import { t } from '../utils/i18n';
import { useEffect } from 'react';
export const Spinner = () => <div className="spinner" aria-label={t('Loading')} />;
export const Empty = ({ text = 'Nothing here yet.' }) => <div className="empty">{t(text)}</div>;
export const ErrorBox = ({ msg, retry }) => <div className="errbox">{msg} {retry && <button className="btn sm" onClick={retry}>{t('Try again')}</button>}</div>;
export const Badge = ({ kind = 'gray', children }) => <span className={`badge ${kind}`}>{typeof children === 'string' ? t(children) : children}</span>;
export const Stat = ({ label, value, tone }) => <div className={`card stat ${tone || ''}`}><span>{label}</span><strong>{value}</strong></div>;
export const StockBadge = ({ s }) => s === 'out' ? <Badge kind="red">Out of Stock</Badge> : s === 'low' ? <Badge kind="amber">Low Stock</Badge> : <Badge kind="green">In Stock</Badge>;
export function State({ loading, error, retry, children }) {
  if (loading) return <Spinner />;
  if (error) return <ErrorBox msg={error} retry={retry} />;
  return children;
}
export function Modal({ title, onClose, children }) {
  useEffect(() => { const k = (e) => e.key === 'Escape' && onClose(); addEventListener('keydown', k); return () => removeEventListener('keydown', k); }, [onClose]);
  return (<div className="overlay" onClick={onClose}><div className="modal" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}>
    <header><h3>{title}</h3><button className="x" onClick={onClose} aria-label={t('Close')}>×</button></header>{children}</div></div>);
}
export const Confirm = ({ text, onYes, onNo, busy }) => (
  <Modal title={t('Please confirm')} onClose={onNo}><p>{text}</p>
    <div className="row end"><button className="btn" onClick={onNo}>{t('Cancel')}</button><button className="btn danger" disabled={busy} onClick={onYes}>{busy ? t('Working…') : t('Yes, continue')}</button></div></Modal>
);
