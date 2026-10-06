import api, { unwrap } from './api';
export const reportService = {
  summary: (params) => unwrap(api.get('/reports/summary', { params })),
  employeeSummary: () => unwrap(api.get('/reports/employee-summary')),
};
