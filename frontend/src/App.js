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
  const [authState, setAuthState] = useState(isAuthenticated());

  // 监听localStorage变化，更新认证状态
  useEffect(() => {
    const checkAuth = () => {
      setAuthState(isAuthenticated());
    };

    // 初始检查
    checkAuth();

    // 监听storage事件（跨标签页）
    window.addEventListener('storage', checkAuth);

    // 定期检查（处理同标签页的更新）
    const interval = setInterval(checkAuth, 100);

    return () => {
      window.removeEventListener('storage', checkAuth);
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

