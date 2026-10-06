import { t } from '../utils/i18n';
import { useState } from 'react';
import { ResponsiveContainer, LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';
import { reportService } from '../services/reportService';
import { useFetch } from '../hooks/useFetch';
import { State, Stat } from '../components/ui';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { salesService } from '../services/salesService';
import { productService } from '../services/productService';
import SalesPdfButton from '../components/SalesPdfButton';
import { StockBadge, Empty } from '../components/ui';
import { money, timeOf, stockStatus } from '../utils/format';

const Chart = ({ title, children }) => <div className="card"><h3>{title}</h3><div style={{ height: 240 }}><ResponsiveContainer>{children}</ResponsiveContainer></div></div>;

export function Dashboard({ reports }) {
  const [range, setRange] = useState({ from: '', to: '' });
  const { data: d, loading, error, reload } = useFetch(() => reportService.summary(range), [range.from, range.to]);
  const trend = (d?.trend || []).map((t) => ({ ...t, profit: t.sales - t.expenses }));
  const profit = d ? (reports ? d.total_sales - d.total_expenses : d.today_sales - d.today_expenses) : 0;
  return (<div>
    <div className="pagehead"><h1>{reports ? t('Reports') : t('Dashboard')}</h1>
      {reports && <div className="toolbar"><input type="date" value={range.from} onChange={(e) => setRange({ ...range, from: e.target.value })} /><input type="date" value={range.to} onChange={(e) => setRange({ ...range, to: e.target.value })} /></div>}</div>
    <State loading={loading} error={error} retry={reload}>{d && <>
      <div className="grid4">
        {reports ? <><Stat label={t('Total Sales')} value={money(d.total_sales)} /><Stat label={t('Total Expenses')} value={money(d.total_expenses)} /><Stat label={t('Net Profit')} value={money(profit)} tone={profit >= 0 ? 'good' : 'bad'} /></> :
          <><Stat label={t('Today\'s Sales')} value={money(d.today_sales)} /><Stat label={t('Today\'s Expenses')} value={money(d.today_expenses)} /><Stat label={t('Today\'s Profit')} value={money(profit)} tone={profit >= 0 ? 'good' : 'bad'} />
            <Stat label={t('Total Products')} value={d.products} /><Stat label={t('Low Stock Products')} value={d.low_stock} tone={d.low_stock ? 'bad' : ''} /><Stat label={t('Total Employees')} value={d.employees} />
            <Stat label={t('Current Subscription')} value={d.plan || '-'} /><Stat label={t('Remaining Days')} value={d.days_left ?? '-'} /></>}
      </div>
      <div className="grid2">
        <Chart title={t('Sales, expenses & profit')}><LineChart data={trend}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" /><YAxis /><Tooltip formatter={money} /><Legend />
          <Line dataKey="sales" stroke="#0b6b5d" strokeWidth={2} /><Line dataKey="expenses" stroke="#c0392b" strokeWidth={2} /><Line dataKey="profit" stroke="#e8a317" strokeWidth={2} /></LineChart></Chart>
        <Chart title={t('Top selling products')}><BarChart data={d.top_products || []}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="qty" fill="#0b6b5d" /></BarChart></Chart>
        <Chart title={t('Sales by employee')}><BarChart data={d.by_employee || []}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis /><Tooltip formatter={money} /><Bar dataKey="total" fill="#e8a317" /></BarChart></Chart>
        <Chart title={t('Expenses by category')}><BarChart data={d.by_category || []}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="category" /><YAxis /><Tooltip formatter={money} /><Bar dataKey="total" fill="#c0392b" /></BarChart></Chart>
      </div></>}</State></div>);
}

export function EmployeeDashboard() {
  const { user } = useAuth();
  const sum = useFetch(reportService.employeeSummary), mine = useFetch(() => salesService.mine()), prods = useFetch(() => productService.list());
  const today = mine.data?.items || mine.data || [];
  const low = (prods.data?.items || prods.data || []).filter((p) => p.stock <= 10);
  const total = today.reduce((a, r) => a + Number(r.total), 0);
  const loading = sum.loading || mine.loading || prods.loading, error = sum.error || mine.error || prods.error;
  return (<div>
    <div className="pagehead"><div><h1>{t('Dashboard')}</h1><p className="muted">{user.shop_name}</p></div><Link className="btn primary lg" to="/employee/sales/new">{t('New sale')}</Link></div>
    <State loading={loading} error={error} retry={() => { sum.reload(); mine.reload(); prods.reload(); }}>
      <div className="grid4"><Stat label={t('Today\'s Sales')} value={money(total)} tone="good" /><Stat label={t('Sales made today')} value={today.length} /><Stat label={t('Last 7 days')} value={money(sum.data?.week_total)} />
        <Stat label={t('Products available')} value={(prods.data?.items || prods.data || []).filter((p) => p.stock > 0).length} /><Stat label={t('Low stock')} value={low.length} tone={low.length ? 'bad' : ''} /></div>
      <div className="grid2">
        <Chart title={t('My sales, last 7 days')}><BarChart data={sum.data?.trend || []}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" /><YAxis /><Tooltip formatter={money} /><Bar dataKey="total" fill="#0b6b5d" /></BarChart></Chart>
        <div className="card"><h3>{t('Low stock in your shop')}</h3>{low.length === 0 ? <Empty text={t('All products have enough stock.')} /> :
          <table><tbody>{low.slice(0, 6).map((p) => <tr key={p.id}><td>{p.name}</td><td>{p.stock}</td><td><StockBadge s={stockStatus(p.stock)} /></td></tr>)}</tbody></table>}</div>
      </div>
      <div className="card"><h3>{t('Latest sales today')}</h3>{today.length === 0 ? <Empty text={t('No sales yet today.')} /> :
        <div className="tablewrap"><table><tbody>{today.slice(0, 5).map((r) => <tr key={r.id}><td>🔒 {timeOf(r.created_at)}</td><td>{r.product_name}</td><td>{r.quantity}</td><td>{money(r.total)}</td></tr>)}</tbody></table></div>}</div>
      <div className="card" style={{ marginTop: '1rem' }}><h3>{t('Sales report (PDF)')}</h3><p className="muted">{t('Download everything you sold for a period. Leave dates empty for today.')}</p><SalesPdfButton /></div>
    </State></div>);
}
