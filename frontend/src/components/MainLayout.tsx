import React from 'react';
import { Layout, Menu, Dropdown, Avatar, Space } from 'antd';
import {
  HomeOutlined,
  ProjectOutlined,
  CarOutlined,
  WarningOutlined,
  DesktopOutlined,
  BarChartOutlined,
  ReadOutlined,
  FileTextOutlined,
  FolderOutlined,
  SyncOutlined,
  SettingOutlined,
  UserOutlined,
  BankOutlined,
  DatabaseOutlined,
  ShopOutlined,
  AppstoreOutlined,
  FileZipOutlined,
  BookOutlined,
  AuditOutlined,
  LogoutOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { authService } from '../services/auth';

const { Header, Sider, Content } = Layout;

// 菜单结构（业务模块在前，系统管理置底）
const menuItems = [
  { key: '/dashboard', icon: <HomeOutlined />, label: '首页' },
  { key: '/project-plan', icon: <ProjectOutlined />, label: '项目计划' },
  { key: '/delivery-progress', icon: <CarOutlined />, label: '交付进展' },
  { key: '/risk-management', icon: <WarningOutlined />, label: '风险管理' },
  { key: '/device-info', icon: <DesktopOutlined />, label: '设备信息' },
  { key: '/school-dashboard', icon: <BarChartOutlined />, label: '学校看板' },
  { key: '/training-management', icon: <ReadOutlined />, label: '培训管理' },
  { key: '/report-management', icon: <FileTextOutlined />, label: '报告管理' },
  { key: '/material-library', icon: <FolderOutlined />, label: '交付材料库' },
  { key: '/project-review', icon: <SyncOutlined />, label: '项目复盘' },
  {
    key: 'system',
    icon: <SettingOutlined />,
    label: '系统管理',
    children: [
      { key: '/users', icon: <UserOutlined />, label: '用户管理' },
      { key: '/schools', icon: <BankOutlined />, label: '学校管理' },
      { key: '/device-systems', icon: <DatabaseOutlined />, label: '设备字典' },
      { key: '/suppliers', icon: <ShopOutlined />, label: '供应商管理' },
      { key: '/production-lines', icon: <AppstoreOutlined />, label: '产线类型管理' },
      { key: '/templates', icon: <FileZipOutlined />, label: '模板管理' },
      { key: '/dict-items', icon: <BookOutlined />, label: '数据字典' },
      { key: '/project-info', icon: <ProjectOutlined />, label: '项目信息' },
      { key: '/operation-logs', icon: <AuditOutlined />, label: '操作日志' },
    ],
  },
];

const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const userMenu = {
    items: [
      { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', onClick: () => authService.logout() },
    ],
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={220} theme="dark">
        <div style={{ height: 48, margin: 16, lineHeight: '48px', textAlign: 'center', fontSize: 16, fontWeight: 600, color: '#fff' }}>
          GX项目管理
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          defaultOpenKeys={['system']}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
          <span style={{ fontSize: 18, fontWeight: 600 }}>高新区"AI+教育"项目交付管理系统</span>
          <Dropdown menu={userMenu} placement="bottomRight">
            <Space style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} />
              <span>{JSON.parse(localStorage.getItem('user') || '{}').real_name || '用户'}</span>
            </Space>
          </Dropdown>
        </Header>
        <Content style={{ margin: 0, background: '#f0f2f5' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
