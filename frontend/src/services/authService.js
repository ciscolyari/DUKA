import api, { unwrap } from './api';
export const authService = {
  // Role is decided by the backend. Expected response: { access_token, user: { id, full_name, role: 'admin'|'employee', shop_name } }
  login: (username, password) => unwrap(api.post('/auth/login', { username, password })),
  registerShop: (data) => unwrap(api.post('/auth/register', data)),
  forgotPassword: (username) => unwrap(api.post('/auth/forgot-password', { username })),
  resetPassword: (token, new_password) => unwrap(api.post('/auth/reset-password', { token, new_password })),
  me: () => unwrap(api.get('/auth/me')),
  changePassword: (data) => unwrap(api.post('/auth/change-password', data)),
};
