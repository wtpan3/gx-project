import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import UserManagement from './pages/UserManagement';
import ProjectPlan from './pages/ProjectPlan';
import Placeholder from './pages/Placeholder';
import MainLayout from './components/MainLayout';
import PrivateRoute from './components/PrivateRoute';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        {/* 登录后的主框架，带侧边菜单 */}
        <Route
          element={
            <PrivateRoute>
              <MainLayout />
            </PrivateRoute>
          }
        >
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/users" element={<UserManagement />} />
          {/* 以下为待开发模块，先用占位页 */}
          <Route path="/schools" element={<Placeholder />} />
          <Route path="/device-systems" element={<Placeholder />} />
          <Route path="/suppliers" element={<Placeholder />} />
          <Route path="/templates" element={<Placeholder />} />
          <Route path="/dict" element={<Placeholder />} />
          <Route path="/project-info" element={<Placeholder />} />
          <Route path="/logs" element={<Placeholder />} />
          <Route path="/plans" element={<ProjectPlan />} />
          <Route path="/devices" element={<Placeholder />} />
          <Route path="/delivery" element={<Placeholder />} />
          <Route path="/trainings" element={<Placeholder />} />
          <Route path="/risks" element={<Placeholder />} />
          <Route path="/reports" element={<Placeholder />} />
          <Route path="/school-board" element={<Placeholder />} />
          <Route path="/materials" element={<Placeholder />} />
          <Route path="/review" element={<Placeholder />} />
        </Route>
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>
    </Router>
  );
}

export default App;
