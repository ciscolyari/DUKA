import { money, dateOf, timeOf } from './format';
// Builds and downloads a PDF of the employee's sales. jsPDF is loaded on demand.
export async function salesPdf({ shop, employee, rows, from, to }) {
  const [{ default: jsPDF }, { default: autoTable }] = await Promise.all([import('jspdf'), import('jspdf-autotable')]);
  const doc = new jsPDF();
  const total = rows.reduce((a, r) => a + Number(r.total), 0), qty = rows.reduce((a, r) => a + Number(r.quantity), 0);
  doc.setFontSize(16); doc.text('DUKA AI - Sales Report', 14, 16);
  doc.setFontSize(10);
  doc.text(`Shop: ${shop}`, 14, 24); doc.text(`Employee: ${employee}`, 14, 29);
  doc.text(`Period: ${from ? dateOf(from) : 'today'}${to ? ' to ' + dateOf(to) : ''}`, 14, 34);
  doc.text(`Generated: ${new Date().toLocaleString('en-GB')}`, 14, 39);
  autoTable(doc, { startY: 44, head: [['Date', 'Time', 'Product', 'Qty', 'Unit price', 'Amount']],
    body: rows.map((r) => [dateOf(r.created_at), timeOf(r.created_at), r.product_name, r.quantity, money(r.unit_price), money(r.total)]),
    foot: [['', '', 'Total', qty, '', money(total)]], headStyles: { fillColor: [11, 107, 93] }, footStyles: { fillColor: [232, 163, 23], textColor: 20 } });
  const by = {}; rows.forEach((r) => { const b = (by[r.product_name] ||= { q: 0, t: 0 }); b.q += Number(r.quantity); b.t += Number(r.total); });
  autoTable(doc, { startY: doc.lastAutoTable.finalY + 10, head: [['Summary by product', 'Qty sold', 'Amount']], body: Object.entries(by).map(([n, b]) => [n, b.q, money(b.t)]), headStyles: { fillColor: [11, 107, 93] } });
  doc.save(`sales-${(from || new Date().toISOString().slice(0, 10))}${to ? '_' + to : ''}.pdf`);
}
