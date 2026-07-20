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
          {/* 首页 */}
          <Route path="/dashboard" element={<Dashboard />} />

          {/* 业务模块 */}
          <Route path="/project-plan" element={<ProjectPlan />} />
          <Route path="/delivery-progress" element={<Placeholder />} />
          <Route path="/risk-management" element={<Placeholder />} />
          <Route path="/device-info" element={<Placeholder />} />
          <Route path="/school-dashboard" element={<Placeholder />} />
          <Route path="/training-management" element={<Placeholder />} />
          <Route path="/report-management" element={<Placeholder />} />
          <Route path="/material-library" element={<Placeholder />} />
          <Route path="/project-review" element={<Placeholder />} />

          {/* 系统管理模块 */}
          <Route path="/users" element={<UserManagement />} />
          <Route path="/schools" element={<Placeholder />} />
          <Route path="/device-systems" element={<Placeholder />} />
          <Route path="/suppliers" element={<Placeholder />} />
          <Route path="/production-lines" element={<Placeholder />} />
          <Route path="/templates" element={<Placeholder />} />
          <Route path="/dict-items" element={<Placeholder />} />
          <Route path="/project-info" element={<Placeholder />} />
          <Route path="/operation-logs" element={<Placeholder />} />
        </Route>
        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </Router>
  );
}

export default App;
