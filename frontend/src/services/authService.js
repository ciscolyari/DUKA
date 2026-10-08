import api, { unwrap } from './api';
export const authService = {
  // Role is decided by the backend. Expected response: { access_token, user: { id, full_name, role: 'admin'|'employee', shop_name } }
  login: (username, password) => unwrap(api.post('/auth/login', { username, password })),
  registerShop: ({ username, ...data }) => unwrap(api.post('/auth/register', { ...data, email: username })),
  forgotPassword: () => Promise.reject(new Error('Password-reset email is not implemented by the backend yet.')),
  resetPassword: () => Promise.reject(new Error('Password-reset tokens are not implemented by the backend yet.')),
  me: () => unwrap(api.get('/auth/me')),
  changePassword: () => Promise.reject(new Error('Self-service password changes are not implemented by the backend yet.')),
};
