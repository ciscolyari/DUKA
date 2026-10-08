import api, { unwrap } from './api';

const toPlan = (plan) => ({
  ...plan,
  features: Array.isArray(plan.features)
    ? plan.features
    : Object.entries(plan.features || {}).map(([name, value]) => `${name}: ${value}`),
});

export const subscriptionService = {
  async current() {
    let subscription;
    try {
      subscription = await unwrap(api.get('/subscriptions/current'));
    } catch (error) {
      if (
        error.response?.status !== 404 ||
        error.response?.data?.detail !== 'No current subscription'
      ) throw error;
      return null;
    }
    const plans = await subscriptionService.plans();
    const plan = plans.find((item) => item.id === subscription.plan_id);
    return {
      ...subscription,
      start_date: subscription.starts_at,
      expiry_date: subscription.expires_at,
      days_left: subscription.days_remaining,
      price: Number(plan?.price ?? subscription.amount_paid ?? 0),
      payment_status: subscription.status,
    };
  },
  async plans() {
    const plans = await unwrap(api.get('/subscription-plans', {
      params: { active_only: true },
    }));
    return plans.map(toPlan);
  },
  async billing() {
    const records = await unwrap(api.get('/billing'));
    return records.map((record) => ({
      ...record,
      transaction_id: record.transaction_ref,
      status: record.status.toLowerCase() === 'success' ? 'paid' : record.status.toLowerCase(),
      date: record.payment_date,
    }));
  },
};
