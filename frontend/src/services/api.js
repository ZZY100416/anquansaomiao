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
      // 调试：检查token格式
      if (config.url?.includes('dashboard')) {
        console.log('Dashboard请求 - Token已添加:', token.substring(0, 20) + '...', '长度:', token.length);
      }
    } else {
      console.warn('请求未携带token:', config.url);
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
      const errorStr = JSON.stringify(error.response?.data || {});
      
      console.error('收到422错误:', errorMsg, '完整响应:', errorStr);
      
      // 检查是否是JWT token相关错误
      // Flask-JWT-Extended在token无效时会返回422，错误信息可能包含：
      // - "无效的Token: ..."
      // - "Invalid token"
      // - "Token verification failed"
      const isTokenError = 
        errorMsg.includes('Token') || 
        errorMsg.includes('token') || 
        errorMsg.includes('无效的Token') ||
        errorMsg.includes('无效的') ||
        errorMsg.includes('缺少Token') ||
        errorMsg.includes('Token已过期') ||
        errorMsg.includes('JWT') ||
        errorStr.toLowerCase().includes('invalid token') ||
        errorStr.toLowerCase().includes('jwt') ||
        (errorStr.toLowerCase().includes('token') && errorStr.toLowerCase().includes('invalid'));
      
      if (isTokenError) {
        console.error('JWT验证失败，清除token并跳转登录:', errorMsg);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        // 触发认证状态变化事件
        window.dispatchEvent(new Event('authChange'));
        // 延迟跳转，避免与其他逻辑冲突
        setTimeout(() => {
          if (!localStorage.getItem('token')) {
            window.location.href = '/login';
          }
        }, 100);
      } else {
        // 其他422错误（可能是业务逻辑错误），只记录日志，不跳转
        console.warn('422错误（非token错误，不跳转）:', errorMsg);
        // 不处理，让组件自己处理错误
      }
    }
    return Promise.reject(error);
  }
);

export default api;

