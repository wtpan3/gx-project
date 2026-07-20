import React from 'react';
import { Layout, Menu, Dropdown, Avatar, Space } from 'antd';
import {
  DashboardOutlined,
  SettingOutlined,
  ProjectOutlined,
  DesktopOutlined,
  CarryOutOutlined,
  ReadOutlined,
  WarningOutlined,
  FileTextOutlined,
  DatabaseOutlined,
  UserOutlined,
  LogoutOutlined,
  TeamOutlined,
  ShopOutlined,
  FileZipOutlined,
  BookOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { authService } from '../services/auth';

const { Header, Sider, Content } = Layout;

// 菜单结构（业务模块在前，系统管理置底）
const menuItems = [
  { key: '/dashboard', icon: <DashboardOutlined />, label: '首页' },
  { key: '/plans', icon: <ProjectOutlined />, label: '项目计划' },
  { key: '/delivery', icon: <CarryOutOutlined />, label: '交付进展' },
  { key: '/risks', icon: <WarningOutlined />, label: '风险管理' },
  { key: '/devices', icon: <DesktopOutlined />, label: '设备信息' },
  { key: '/school-board', icon: <BookOutlined />, label: '学校看板' },
  { key: '/trainings', icon: <ReadOutlined />, label: '培训管理' },
  { key: '/reports', icon: <FileTextOutlined />, label: '报告管理' },
  { key: '/materials', icon: <FileZipOutlined />, label: '交付材料库' },
  { key: '/review', icon: <CarryOutOutlined />, label: '项目复盘' },
  {
    key: 'system',
    icon: <SettingOutlined />,
    label: '系统管理',
    children: [
      { key: '/users', icon: <TeamOutlined />, label: '用户管理' },
      { key: '/schools', icon: <BookOutlined />, label: '学校管理' },
      { key: '/device-systems', icon: <DatabaseOutlined />, label: '设备系统字典' },
      { key: '/suppliers', icon: <ShopOutlined />, label: '供应商管理' },
      { key: '/templates', icon: <FileTextOutlined />, label: '模板管理' },
      { key: '/dict', icon: <DatabaseOutlined />, label: '数据字典' },
      { key: '/project-info', icon: <ProjectOutlined />, label: '项目信息' },
      { key: '/logs', icon: <FileTextOutlined />, label: '操作日志' },
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
      <Sider width={220} theme="dark" style={{ overflow: 'auto', height: '100vh', position: 'sticky', top: 0, left: 0 }}>
        <div style={{ height: 48, margin: 16, color: '#fff', fontSize: 16, fontWeight: 600, textAlign: 'center', lineHeight: '48px' }}>
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
