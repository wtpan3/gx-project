import axios from 'axios';

// API基础地址：
// - 生产环境 .env.production 设为空 → 用相对路径，请求走 Nginx 反代（同源，无CORS）
// - 开发环境 .env.development 设为 http://127.0.0.1:8000
// 注意：用 !== undefined 判断，空字符串是合法值（相对路径），不能用 || 回退
const apiBase = process.env.REACT_APP_API_URL !== undefined
  ? process.env.REACT_APP_API_URL
  : 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: apiBase,
  timeout: 30000,
});

// 请求拦截器：自动注入token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：401自动跳转登录
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
