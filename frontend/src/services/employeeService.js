import api, { unwrap } from './api';
import { crud } from './crud';
export const employeeService = { ...crud('/employees'), resetPassword: (id, new_password) => unwrap(api.patch(`/employees/${id}/password`, { new_password })), setActive: (id, is_active) => unwrap(api.patch(`/employees/${id}/status`, { is_active })) };
