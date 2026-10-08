import { t } from '../utils/i18n';
import { useState } from 'react';
import { productService } from '../services/productService';
import { employeeService } from '../services/employeeService';
import { expenseService } from '../services/expenseService';
import { salesService } from '../services/salesService';
import { subscriptionService } from '../services/subscriptionService';
import { useToast } from '../context/ToastContext';
import { useNavigate } from 'react-router-dom';
import { shopService } from '../services/shopService';
import { useShop } from '../context/ShopContext';
import DataPage from '../components/DataPage';
import { Badge, StockBadge, Stat, Modal } from '../components/ui';
import { money, dateOf, timeOf, stockStatus, errMsg } from '../utils/format';

function ResetPassword({ emp }) {
  const toast = useToast();
  const [open, setOpen] = useState(false), [pw, setPw] = useState(''), [pw2, setPw2] = useState(''), [busy, setBusy] = useState(false);
  const close = () => { setOpen(false); setPw(''); setPw2(''); };
  const submit = async (e) => {
    e.preventDefault(); if (pw !== pw2) return toast(t('Passwords do not match'), 'err');
    setBusy(true);
    try { await employeeService.resetPassword(emp.id, pw); toast(`Password changed for ${emp.full_name}`); close(); } catch (er) { toast(errMsg(er), 'err'); } finally { setBusy(false); }
  };
  return (<><button className="btn sm" onClick={() => setOpen(true)}>{t('Reset password')}</button>
    {open && <Modal title={`${t('New password for')} ${emp.full_name}`} onClose={close}><form className="form" onSubmit={submit}>
      <label>{t('New password')}<input type="password" required minLength={6} autoComplete="new-password" value={pw} onChange={(e) => setPw(e.target.value)} /></label>
      <label>{t('Confirm password')}<input type="password" required autoComplete="new-password" value={pw2} onChange={(e) => setPw2(e.target.value)} /></label>
      <div className="row end"><button type="button" className="btn" onClick={close}>{t('Cancel')}</button><button className="btn primary" disabled={busy}>{busy ? t('Saving…') : t('Change password')}</button></div></form></Modal>}</>);
}

const cat = [
  { value: 'rent', label: 'Rent' },
  { value: 'electricity', label: 'Electricity' },
  { value: 'water', label: 'Water' },
  { value: 'waste', label: 'Waste' },
  { value: 'transport', label: 'Transport' },
  { value: 'supplies', label: 'Supplies' },
  { value: 'salary', label: 'Salaries' },
  { value: 'other', label: 'Other' },
];

export function Products({ admin }) {
  return <DataPage title={t('Products')} service={productService} canAdd={admin} canEdit={admin} canDelete={admin} canView searchKeys={['name', 'description']}
    filters={[{ name: 'stock', label: t('Stock'), options: [{ value: 'low', label: t('Low stock') }, { value: 'out', label: t('Out of stock') }] }]}
    fields={[{ name: 'name', label: t('Product name'), required: true }, { name: 'description', label: t('Description') }, { name: 'price', label: t('Selling price (TZS)'), type: 'number', required: true }, { name: 'stock', label: t('Stock quantity'), type: 'number', required: true }]}
    columns={[{ key: 'name', label: t('Product') }, { key: 'description', label: t('Description') }, { key: 'price', label: t('Price'), render: (r) => money(r.price) },
      { key: 'stock', label: t('Stock'), render: (r) => <>{r.stock} <StockBadge s={stockStatus(r.stock)} /></> },
      { key: 'created_at', label: t('Created'), render: (r) => dateOf(r.created_at) }, { key: 'updated_at', label: t('Updated'), render: (r) => dateOf(r.updated_at) }]} />;
}
export const Inventory = ({ employee = false }) => <DataPage title={t('Inventory')} listFn={employee ? salesService.myInventory : salesService.inventory} searchKeys={['name']}
  columns={[{ key: 'name', label: t('Product') }, { key: 'stock', label: t('Current stock') }, { key: 'sold_today', label: t('Sold today') }, { key: 'stock2', label: t('Remaining'), render: (r) => r.stock }, { key: 's', label: t('Status'), render: (r) => <StockBadge s={stockStatus(r.stock)} /> }]} />;
export const Sales = () => <DataPage title={t('Sales')} listFn={salesService.all} searchKeys={['product_name', 'employee_name']}
  filters={[{ name: 'date', label: t('Date'), type: 'date' }, { name: 'employee', label: t('Employee ID'), type: 'number' }]}
  columns={[{ key: 'id', label: t('Sale ID') }, { key: 'employee_name', label: t('Employee') }, { key: 'product_name', label: t('Product') }, { key: 'quantity', label: t('Qty') },
    { key: 'unit_price', label: t('Unit price'), render: (r) => money(r.unit_price) }, { key: 'total', label: t('Total'), render: (r) => money(r.total) },
    { key: 'd', label: t('Date'), render: (r) => dateOf(r.created_at) }, { key: 't', label: t('Time'), render: (r) => timeOf(r.created_at) }, { key: 'status', label: t('Status'), render: () => <Badge kind="green">{t('🔒 Locked')}</Badge> }]} />;
export const Employees = () => {
  const toast = useToast(); const { shop } = useShop();
  const same = (a, b) => String(a || '').trim().toLowerCase() === String(b || '').trim().toLowerCase();
  return <DataPage title={t('Employees')}
    validate={(v, all, id) => all.some((e) => e.id !== id && same(e.username, v.username)) ? 'This email is already used. Choose a different one.' : null} service={employeeService} summary={() => <p className="muted">{t('Employees are assigned to your shop: ')}<b>{shop?.name}</b>.</p>} canAdd canEdit canView searchKeys={['full_name', 'username']}
    fields={[{ name: 'full_name', label: t('Full name'), required: true }, { name: 'username', label: t('Email (must be unique)'), required: true }, { name: 'password', label: t('Password'), type: 'password', required: true, createOnly: true }]}
    columns={[{ key: 'full_name', label: t('Name') }, { key: 'username', label: t('Email') }, { key: 'shop_id', label: t('Shop ID') }, { key: 's', label: t('Status'), render: (r) => <Badge kind={r.is_active ? 'green' : 'gray'}>{r.is_active ? t('Active') : t('Inactive')}</Badge> },
      { key: 'created_at', label: t('Created'), render: (r) => dateOf(r.created_at) }]}
    extraActions={(r, reload) => <><ResetPassword emp={r} /><button className="btn sm" onClick={async () => { try { await employeeService.setActive(r.id, !r.is_active); toast(r.is_active ? t('Employee deactivated') : t('Employee activated')); reload(); } catch (e) { toast(errMsg(e), 'err'); } }}>{r.is_active ? t('Deactivate') : t('Activate')}</button></>} />;
};
export const Expenses = ({ employee }) => <DataPage title={employee ? t('My Expenses') : t('Expenses (Matumizi)')} service={expenseService} defaults={{ date: new Date().toISOString().slice(0, 10) }} canAdd canEdit={!employee} canDelete={!employee} canView searchKeys={['title', 'description']}
  filters={[{ name: 'date', label: t('Date'), type: 'date' }, { name: 'category', label: t('Category'), options: cat }]}
  summary={(rows) => <div className="grid4"><Stat label={t('Total (selected date)')} value={money(rows.reduce((sum, row) => sum + Number(row.amount), 0))} /></div>}
  fields={[{ name: 'title', label: t('Expense name'), required: true }, { name: 'category', label: t('Category'), type: 'select', options: cat, required: true }, { name: 'amount', label: t('Amount (TZS)'), type: 'number', required: true }, { name: 'notes', label: t('Notes') }]}
  columns={[{ key: 'id', label: t('ID') }, { key: 'title', label: t('Expense') }, { key: 'category', label: t('Category') }, { key: 'amount', label: t('Amount'), render: (r) => money(r.amount) }, { key: 'date', label: t('Date'), render: (r) => dateOf(r.date) }, { key: 'recorded_by', label: t('Recorded by') }]} />;
export const Billing = () => <DataPage title={t('Billing History')} listFn={subscriptionService.billing}
  columns={[{ key: 'transaction_id', label: t('Transaction ID') }, { key: 'plan', label: t('Plan') }, { key: 'amount', label: t('Amount'), render: (r) => money(r.amount) }, { key: 'currency', label: t('Currency') },
    { key: 'status', label: t('Status'), render: (r) => <Badge kind={{ paid: 'green', pending: 'amber', failed: 'red', cancelled: 'gray' }[r.status]}>{r.status}</Badge> }, { key: 'date', label: t('Date'), render: (r) => dateOf(r.date) }]}
  canView />;

export const Shops = () => {
  const { select, reload, shop } = useShop(); const nav = useNavigate();
  return <DataPage title={t('Shop')} service={shopService} onChange={reload} canEdit canView searchKeys={['name', 'address']}
    fields={[{ name: 'name', label: t('Shop name'), required: true }, { name: 'address', label: t('Location') }]}
    columns={[{ key: 'name', label: t('Shop'), render: (r) => <>{r.name} {String(shop?.id) === String(r.id) && <Badge kind="green">{t('Current')}</Badge>}</> }, { key: 'address', label: t('Location') }, { key: 'created_at', label: t('Created'), render: (r) => dateOf(r.created_at) }]}
    extraActions={(r) => <button className="btn sm primary" onClick={() => { select(r.id); nav('/admin/dashboard'); }}>{t('Open')}</button>} />;
};
