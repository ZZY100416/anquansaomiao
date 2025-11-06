import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/Layout/MainLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import Scans from './pages/Scans';
import Reports from './pages/Reports';
import RASPEvents from './pages/RASPEvents';
import { useAuth } from './services/authService';

function App() {
  const { isAuthenticated } = useAuth();
  const [authState, setAuthState] = useState(() => {
    // 初始状态：检查localStorage中是否有token
    return !!localStorage.getItem('token');
  });

  // 监听localStorage变化，更新认证状态
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      const authenticated = !!token;
      console.log('检查认证状态:', authenticated ? '已认证' : '未认证', token ? 'Token存在' : 'Token不存在');
      setAuthState(authenticated);
    };

    // 初始检查
    checkAuth();

    // 监听storage事件（跨标签页）
    window.addEventListener('storage', checkAuth);

    // 监听自定义事件（同标签页登录/登出）
    const handleAuthChange = () => {
      // 立即检查并更新状态
      console.log('收到authChange事件，更新认证状态');
      checkAuth();
    };
    window.addEventListener('authChange', handleAuthChange);

    // 定期检查（降低频率，避免过于频繁）
    const interval = setInterval(checkAuth, 3000);

    return () => {
      window.removeEventListener('storage', checkAuth);
      window.removeEventListener('authChange', handleAuthChange);
      clearInterval(interval);
    };
  }, []);

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/*"
        element={
          authState ? (
            <MainLayout>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/projects" element={<Projects />} />
                <Route path="/scans" element={<Scans />} />
                <Route path="/rasp" element={<RASPEvents />} />
                <Route path="/reports" element={<Reports />} />
              </Routes>
            </MainLayout>
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
    </Routes>
  );
}

export default App;

