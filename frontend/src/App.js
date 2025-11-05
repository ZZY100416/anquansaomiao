import React from 'react';
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

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/*"
        element={
          isAuthenticated() ? (
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

