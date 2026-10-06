import api, { unwrap } from './api';
// Generic REST helper. Adjust `base` paths to match your FastAPI routers.
export const crud = (base) => ({
  list: (params) => unwrap(api.get(base, { params })),
  get: (id) => unwrap(api.get(`${base}/${id}`)),
  create: (data) => unwrap(api.post(base, data)),
  update: (id, data) => unwrap(api.put(`${base}/${id}`, data)),
  remove: (id) => unwrap(api.delete(`${base}/${id}`)),
});
