import { t } from '../utils/i18n';
import { useState } from 'react';
import { salesService } from '../services/salesService';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { salesPdf } from '../utils/pdf';
import { errMsg } from '../utils/format';
export default function SalesPdfButton() {
  const { user } = useAuth(); const toast = useToast();
  const [from, setFrom] = useState(''), [to, setTo] = useState(''), [busy, setBusy] = useState(false);
  const go = async () => {
    setBusy(true);
    try {
      const r = await salesService.mine({ from: from || undefined, to: to || undefined }); const rows = r.items || r;
      if (!rows.length) return toast(t('No sales in this period.'), 'err');
      await salesPdf({ shop: user.shop_name, employee: user.full_name, rows, from, to }); toast(t('PDF ready'));
    } catch (e) { toast(errMsg(e), 'err'); } finally { setBusy(false); }
  };
  return (<div className="toolbar"><label className="inl">{t('From')}<input type="date" value={from} onChange={(e) => setFrom(e.target.value)} /></label>
    <label className="inl">{t('To')}<input type="date" value={to} onChange={(e) => setTo(e.target.value)} /></label>
    <button className="btn primary" onClick={go} disabled={busy}>{busy ? t('Preparing…') : t('Download PDF report')}</button></div>);
}
