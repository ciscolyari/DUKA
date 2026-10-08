import api, { unwrap } from './api';

const toEmployee = (employee) => ({
  ...employee,
  username: employee.email,
  is_active: employee.active,
});

const toPayload = (data) => ({
  ...(data.full_name === undefined ? {} : { full_name: data.full_name }),
  ...(data.username === undefined ? {} : { email: data.username }),
  ...(data.password === undefined ? {} : { password: data.password }),
  ...(data.active === undefined && data.is_active === undefined
    ? {}
    : { active: data.active ?? data.is_active }),
  ...(data.role === undefined ? {} : { role: data.role }),
});

export const employeeService = {
  async list(params = {}) {
    const employees = await unwrap(api.get('/employees', {
      params: { active_only: params.active_only ?? false },
    }));
    return employees.map(toEmployee);
  },
  async get(id) {
    return toEmployee(await unwrap(api.get(`/employees/${id}`)));
  },
  async create(data) {
    return toEmployee(await unwrap(api.post('/employees', {
      ...toPayload(data),
      role: 'employee',
    })));
  },
  async update(id, data) {
    return toEmployee(await unwrap(api.put(`/employees/${id}`, toPayload(data))));
  },
  async remove(id) {
    return toEmployee(await unwrap(api.delete(`/employees/${id}`)));
  },
  resetPassword: (id, password) => employeeService.update(id, { password }),
  setActive: (id, active) => employeeService.update(id, { active }),
};
