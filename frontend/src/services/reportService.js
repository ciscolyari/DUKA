import api, { unwrap } from './api';

export const reportService = {
  async summary(params = {}, reports = false) {
    return unwrap(api.get('/reports/summary', {
      params: {
        from_date: params.from || undefined,
        to_date: params.to || undefined,
        reports,
      },
    }));
  },
  async employeeSummary() {
    return unwrap(api.get('/reports/employee-summary'));
  },
};
