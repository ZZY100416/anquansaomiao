import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 处理401未授权错误
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    // 处理422 token验证失败错误
    if (error.response?.status === 422) {
      const errorMsg = error.response?.data?.error || '';
      console.error('收到422错误:', errorMsg);
      
      // 只有明确的token错误才清除token
      const isTokenError = errorMsg.includes('Token') || 
                          errorMsg.includes('token') || 
                          errorMsg.includes('无效的Token') ||
                          errorMsg.includes('无效的') ||
                          errorMsg.toLowerCase().includes('invalid token');
      
      if (isTokenError) {
        console.error('JWT验证失败，清除token:', errorMsg);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        // 触发认证状态变化事件
        window.dispatchEvent(new Event('authChange'));
        window.location.href = '/login';
      } else {
        // 其他422错误（可能是业务逻辑错误），只记录日志，不跳转
        console.warn('422错误（非token错误）:', errorMsg);
      }
    }
    return Promise.reject(error);
  }
);

export default api;

