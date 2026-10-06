export const money = (n) => `TZS ${Number(n || 0).toLocaleString('en-US')}`;
export const dateOf = (d) => (d ? new Date(d).toLocaleDateString('en-GB') : '-');
export const timeOf = (d) => (d ? new Date(d).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }) : '-');
export const stockStatus = (q, low = 10) => (q <= 0 ? 'out' : q <= low ? 'low' : 'in');
export const errMsg = (e) => e?.userMessage || e?.message || 'Unexpected error';
