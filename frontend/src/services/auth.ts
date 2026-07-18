import api from './api';

export interface User {
  id: number;
  username: string;
  real_name: string;
  role: string;
  phone: string;
  email: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export const authService = {
  // 获取当前用户信息
  getMe: () => api.get<User>('/api/v1/auth/me'),

  // 登出（清除本地token并跳转登录页）
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  },

  // 修改密码（请求体传参，不走URL）
  changePassword: (oldPassword: string, newPassword: string) =>
    api.put('/api/v1/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    }),
};
