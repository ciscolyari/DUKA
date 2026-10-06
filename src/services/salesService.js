import api, { unwrap } from './api';
export const salesService = {
  all: (params) => unwrap(api.get('/sales', { params })),     // admin
  mine: (params) => unwrap(api.get('/sales/me', { params })), // employee
  create: (data) => unwrap(api.post('/sales', data)),         // { product_id, quantity } - backend validates stock, deducts, locks
  inventory: () => unwrap(api.get('/inventory')),
};
