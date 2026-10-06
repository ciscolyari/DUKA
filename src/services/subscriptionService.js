import api, { unwrap } from './api';
export const subscriptionService = {
  current: () => unwrap(api.get('/subscription')),
  plans: () => unwrap(api.get('/subscription/plans')),
  billing: () => unwrap(api.get('/subscription/billing')),
};
