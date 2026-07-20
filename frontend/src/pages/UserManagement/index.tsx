import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, message, Popconfirm, Space } from 'antd';
import { PlusOutlined, EditOutlined, KeyOutlined, LockOutlined, StopOutlined, CheckCircleOutlined } from '@ant-design/icons';
import api from '../../services/api';

interface User {
  id: number;
  username: string;
  real_name: string;
  role: string;
  phone: string;
  email: string;
  status: string;
  created_at: string;
}

const ROLE_MAP: Record<string, string> = {
  admin: '管理员',
  project_manager: '项目经理',
  campus_manager: '校园经理',
};

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [form] = Form.useForm();
  // 修改密码弹框
  const [pwdModalVisible, setPwdModalVisible] = useState(false);
  const [pwdUser, setPwdUser] = useState<User | null>(null);
  const [pwdForm] = Form.useForm();

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/v1/users');
      setUsers(res.data.items);
    } catch (error) {
      message.error('加载用户列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleSubmit = async (values: any) => {
    try {
      if (editingUser) {
        await api.put(`/api/v1/users/${editingUser.id}`, values);
        message.success('更新成功');
      } else {
        await api.post('/api/v1/users', values);
        message.success('创建成功');
      }
      setModalVisible(false);
      form.resetFields();
      setEditingUser(null);
      fetchUsers();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  // 切换启用/停用状态
  const handleToggleStatus = async (record: User) => {
    const nextStatus = record.status === '启用' ? '停用' : '启用';
    try {
      await api.put(`/api/v1/users/${record.id}`, { status: nextStatus });
      message.success(`已${nextStatus}`);
      fetchUsers();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  const handleResetPassword = async (id: number) => {
    try {
      await api.post(`/api/v1/users/${id}/reset-password`);
      message.success('密码已重置为 Admin@2026');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '重置失败');
    }
  };

  // 提交修改密码（指定新密码）
  const handleSetPassword = async (values: { new_password: string }) => {
    if (!pwdUser) return;
    try {
      await api.post(`/api/v1/users/${pwdUser.id}/set-password`, { new_password: values.new_password });
      message.success('密码修改成功');
      setPwdModalVisible(false);
      pwdForm.resetFields();
      setPwdUser(null);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '修改失败');
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '用户名', dataIndex: 'username' },
    { title: '姓名', dataIndex: 'real_name' },
    { title: '角色', dataIndex: 'role', render: (v: string) => ROLE_MAP[v] || v },
    { title: '手机号', dataIndex: 'phone' },
    { title: '邮箱', dataIndex: 'email' },
    { title: '状态', dataIndex: 'status', render: (v: string) => <span style={{ color: v === '启用' ? 'green' : 'red' }}>{v}</span> },
    {
      title: '操作',
      width: 380,
      render: (_: any, record: User) => (
        <Space wrap>
          <Button size="small" icon={<EditOutlined />} onClick={() => { setEditingUser(record); form.setFieldsValue(record); setModalVisible(true); }}>编辑</Button>
          <Button size="small" icon={<LockOutlined />} onClick={() => { setPwdUser(record); pwdForm.resetFields(); setPwdModalVisible(true); }}>修改密码</Button>
          <Popconfirm title="确认重置为默认密码 Admin@2026？" onConfirm={() => handleResetPassword(record.id)}>
            <Button size="small" icon={<KeyOutlined />}>重置密码</Button>
          </Popconfirm>
          {record.status === '启用' ? (
            <Popconfirm title="确认停用该用户？" onConfirm={() => handleToggleStatus(record)}>
              <Button size="small" danger icon={<StopOutlined />}>停用</Button>
            </Popconfirm>
          ) : (
            <Popconfirm title="确认启用该用户？" onConfirm={() => handleToggleStatus(record)}>
              <Button size="small" type="primary" ghost icon={<CheckCircleOutlined />}>启用</Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingUser(null); form.resetFields(); setModalVisible(true); }} style={{ marginBottom: 16 }}>新增用户</Button>
      <Table columns={columns} dataSource={users} rowKey="id" loading={loading} />
      <Modal
        title={editingUser ? '编辑用户' : '新增用户'}
        open={modalVisible}
        onCancel={() => { setModalVisible(false); form.resetFields(); setEditingUser(null); }}
        footer={null}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="username" label="用户名" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input disabled={!!editingUser} />
          </Form.Item>
          {!editingUser && (
            <Form.Item name="password" label="密码" rules={[{ required: true, min: 6, message: '密码至少6位' }]}>
              <Input.Password />
            </Form.Item>
          )}
          <Form.Item name="real_name" label="姓名" rules={[{ required: true, message: '请输入姓名' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="role" label="角色" rules={[{ required: true, message: '请选择角色' }]}>
            <Select options={[{ label: '管理员', value: 'admin' }, { label: '项目经理', value: 'project_manager' }, { label: '校园经理', value: 'campus_manager' }]} />
          </Form.Item>
          <Form.Item name="phone" label="手机号" rules={[{ required: true, message: '请输入手机号' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="email" label="邮箱" rules={[{ required: true, type: 'email', message: '请输入有效邮箱' }]}>
            <Input />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>提交</Button>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`修改密码${pwdUser ? ' - ' + pwdUser.real_name : ''}`}
        open={pwdModalVisible}
        onCancel={() => { setPwdModalVisible(false); pwdForm.resetFields(); setPwdUser(null); }}
        footer={null}
        destroyOnHidden
      >
        <Form form={pwdForm} layout="vertical" onFinish={handleSetPassword}>
          <Form.Item name="new_password" label="新密码" rules={[{ required: true, min: 6, message: '密码至少6位' }]}>
            <Input.Password placeholder="请输入新密码（至少6位）" />
          </Form.Item>
          <Form.Item
            name="confirm_password"
            label="确认密码"
            dependencies={['new_password']}
            rules={[
              { required: true, message: '请再次输入新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('new_password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password placeholder="请再次输入新密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>确认修改</Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UserManagement;
