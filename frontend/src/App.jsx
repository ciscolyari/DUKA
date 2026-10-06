import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import { RequireRole, Forbidden, home } from './routes/Guards';
import AppLayout from './layouts/AppLayout';
import { Landing, Login, Register, ForgotPassword, ResetPassword } from './pages/Public';
import { Dashboard, EmployeeDashboard } from './pages/Overview';
import { Shops, Products, Inventory, Sales, Employees, Expenses, Billing } from './pages/Admin';
import Subscription from './pages/Subscription';
import { NewSale, MySales } from './pages/Employee';
import Settings from './pages/Settings';
export default function App() {
  const { user } = useAuth();
  return (<Routes>
    <Route path="/" element={user ? <Navigate to={home(user)} /> : <Landing />} />
    <Route path="/login" element={<Login />} /><Route path="/register" element={<Register />} /><Route path="/forgot-password" element={<ForgotPassword />} /><Route path="/reset-password" element={<ResetPassword />} /><Route path="/403" element={<Forbidden />} />
    <Route path="/admin" element={<RequireRole role="admin" />}><Route element={<AppLayout />}>
      <Route path="dashboard" element={<Dashboard />} /><Route path="shops" element={<Shops />} /><Route path="products" element={<Products admin />} />
      <Route path="inventory" element={<Inventory />} /><Route path="sales" element={<Sales />} />
      <Route path="employees" element={<Employees />} /><Route path="expenses" element={<Expenses />} />
      <Route path="reports" element={<Dashboard reports />} /><Route path="subscription" element={<Subscription />} />
      <Route path="billing" element={<Billing />} /><Route path="settings" element={<Settings admin />} />
    </Route></Route>
    <Route path="/employee" element={<RequireRole role="employee" />}><Route element={<AppLayout />}>
      <Route path="dashboard" element={<EmployeeDashboard />} /><Route path="products" element={<Products />} />
      <Route path="sales/new" element={<NewSale />} /><Route path="sales" element={<MySales />} />
      <Route path="inventory" element={<Inventory />} /><Route path="settings" element={<Settings />} />
    </Route></Route>
    <Route path="*" element={<Navigate to="/" />} />
  </Routes>);
}
