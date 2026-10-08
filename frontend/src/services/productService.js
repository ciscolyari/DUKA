import api, { unwrap } from './api';

const toProduct = (product) => ({
  ...product,
  price: Number(product.selling_price),
  stock: product.stock_quantity,
});

const toPayload = ({ name, description, price, stock, active }) => ({
  name,
  description,
  selling_price: price,
  stock_quantity: stock,
  ...(active === undefined ? {} : { active }),
});

export const productService = {
  async list(params = {}) {
    const query = {
      ...(params.search ? { search: params.search } : {}),
      ...(params.stock === 'low' ? { low_stock_only: true } : {}),
    };
    const products = await unwrap(api.get('/products', { params: query }));
    return products.map(toProduct).filter((product) => params.stock !== 'out' || product.stock === 0);
  },
  async get(id) {
    return toProduct(await unwrap(api.get(`/products/${id}`)));
  },
  async create(data) {
    return toProduct(await unwrap(api.post('/products', toPayload(data))));
  },
  async update(id, data) {
    return toProduct(await unwrap(api.put(`/products/${id}`, toPayload(data))));
  },
  remove: (id) => unwrap(api.delete(`/products/${id}`)),
};
