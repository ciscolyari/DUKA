import api, { unwrap } from './api';
import { productService } from './productService';

const toSale = (sale) => {
  const quantity = sale.items.reduce((sum, item) => sum + item.quantity, 0);
  return {
    ...sale,
    total: Number(sale.total_amount),
    quantity,
    product_name: sale.items.map((item) => item.product_name).filter(Boolean).join(', '),
    unit_price: quantity
      ? Number(sale.total_amount) / quantity
      : 0,
  };
};

const queryParams = ({ date, employee, from, to, ...params } = {}) => ({
  ...params,
  ...(date ? { target_date: date } : {}),
  ...(employee ? { employee_id: employee } : {}),
  ...(from ? { from_date: from } : {}),
  ...(to ? { to_date: to } : {}),
});

const getInventory = async (listSales, params) => {
  const [products, sales] = await Promise.all([
    productService.list(),
    listSales(params),
  ]);
  const soldByProduct = new Map();
  for (const sale of sales) {
    for (const item of sale.items) {
      soldByProduct.set(
        item.product_id,
        (soldByProduct.get(item.product_id) || 0) + item.quantity,
      );
    }
  }
  return products.map((product) => ({
    ...product,
    sold_today: soldByProduct.get(product.id) || 0,
    stock2: product.stock,
  }));
};

export const salesService = {
  async all(params) {
    return (await unwrap(api.get('/sales', { params: queryParams(params) }))).map(toSale);
  },
  async mine(params) {
    return (await unwrap(api.get('/sales/me', { params: queryParams(params) }))).map(toSale);
  },
  async create(data) {
    const sale = await unwrap(api.post('/sales', {
      items: [{ product_id: data.product_id, quantity: data.quantity }],
    }));
    return toSale(sale);
  },
  async inventory(params) {
    return getInventory(salesService.all, params);
  },
  async myInventory(params) {
    return getInventory(salesService.mine, params);
  },
};
