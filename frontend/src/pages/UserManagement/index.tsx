import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, message, Popconfirm, Space } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, KeyOutlined } from '@ant-design/icons';
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

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/api/v1/users/${id}`);
      message.success('已停用');
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
      width: 280,
      render: (_: any, record: User) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => { setEditingUser(record); form.setFieldsValue(record); setModalVisible(true); }}>编辑</Button>
          <Button size="small" icon={<KeyOutlined />} onClick={() => handleResetPassword(record.id)}>重置密码</Button>
          <Popconfirm title="确认停用该用户？" onConfirm={() => handleDelete(record.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} disabled={record.status === '停用'}>停用</Button>
          </Popconfirm>
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
    </div>
  );
};

export default UserManagement;
