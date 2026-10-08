import api, { unwrap } from './api';

const toExpense = (expense) => ({
  ...expense,
  title: expense.description,
  date: expense.created_at,
  recorded_by: expense.recorded_by_name,
});

const toPayload = ({ title, description, category, amount, notes }) => ({
  description: title ?? description,
  ...(category === undefined ? {} : { category: category.toLowerCase() }),
  amount,
  ...(notes === undefined ? {} : { notes }),
});

export const expenseService = {
  async list(params = {}) {
    const { date, category } = params;
    const expenses = await unwrap(api.get('/expenses', {
      params: {
        ...(date ? { target_date: date.slice(0, 10) } : {}),
        ...(category ? { category: category.toLowerCase() } : {}),
      },
    }));
    return expenses.map(toExpense);
  },
  async get(id) {
    return toExpense(await unwrap(api.get(`/expenses/${id}`)));
  },
  async create(data) {
    return toExpense(await unwrap(api.post('/expenses', toPayload(data))));
  },
  async update(id, data) {
    return toExpense(await unwrap(api.put(`/expenses/${id}`, toPayload(data))));
  },
  remove: (id) => unwrap(api.delete(`/expenses/${id}`)),
};
