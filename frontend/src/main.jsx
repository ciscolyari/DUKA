import './i18n';
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { AuthProvider } from './context/AuthContext';
import { ShopProvider } from './context/ShopContext';
import { ToastProvider } from './context/ToastContext';
import './index.css';
ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter><AuthProvider><ShopProvider><ToastProvider><App /></ToastProvider></ShopProvider></AuthProvider></BrowserRouter>
);
