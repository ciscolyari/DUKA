import api, { unwrap } from './api';
export const paymentService = {
  initiate: (data) => unwrap(api.post('/payments', data)),          // -> { transaction_id, status }
  status: (id) => unwrap(api.get(`/payments/${id}`)),               // status: pending|paid|failed|cancelled
};
