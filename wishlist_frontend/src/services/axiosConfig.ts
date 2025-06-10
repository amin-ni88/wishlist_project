import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const BASE_URL = 'http://127.0.0.1:8001'; // آدرس سرور محلی

const axiosConfig = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor برای اضافه کردن توکن احراز هویت
axiosConfig.interceptors.request.use(
  async (config) => {
    try {
      const token = await AsyncStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error getting token from storage:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor برای مدیریت خطاها
axiosConfig.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // اگر خطای 401 (Unauthorized) داشته باشیم
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = await AsyncStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const newAccessToken = response.data.access;
          await AsyncStorage.setItem('access_token', newAccessToken);

          // تکرار درخواست اصلی با توکن جدید
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return axiosConfig(originalRequest);
        }
      } catch (refreshError) {
        // اگر refresh token هم منقضی باشد، کاربر را logout کنیم
        await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
        // اینجا می‌توانید به صفحه لاگین هدایت کنید
        console.error('Token refresh failed:', refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default axiosConfig; 