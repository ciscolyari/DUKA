import api, { unwrap } from './api';

const toShop = (shop) => ({
  ...shop,
  address: shop.location,
});

const toPayload = ({ name, address, location }) => ({
  ...(name === undefined ? {} : { name }),
  ...((address ?? location) === undefined ? {} : { location: address ?? location }),
});

export const shopService = {
  async list() {
    return [toShop(await unwrap(api.get('/shop')))];
  },
  async get() {
    return toShop(await unwrap(api.get('/shop')));
  },
  async update(_id, data) {
    return toShop(await unwrap(api.put('/shop', toPayload(data))));
  },
};
