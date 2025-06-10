import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to add the auth token
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await AsyncStorage.removeItem('access_token');
      await AsyncStorage.removeItem('refresh_token');
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/auth/login/', credentials),
  
  register: (userData: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
  }) => api.post('/auth/register/', userData),
  
  refreshToken: (refresh: string) =>
    api.post('/auth/token/refresh/', { refresh }),
  
  logout: () => api.post('/auth/logout/'),
};

export const wishlistAPI = {
  getWishlists: () => api.get('/wishlists/'),
  
  getWishlist: (id: number) => api.get(`/wishlists/${id}/`),
  
  createWishlist: (data: {
    title: string;
    description?: string;
    occasion_date?: string;
    is_public?: boolean;
  }) => api.post('/wishlists/', data),
  
  updateWishlist: (id: number, data: any) =>
    api.patch(`/wishlists/${id}/`, data),
  
  deleteWishlist: (id: number) => api.delete(`/wishlists/${id}/`),
};

export const itemAPI = {
  getItems: (wishlistId?: number) => {
    const params = wishlistId ? { wishlist: wishlistId } : {};
    return api.get('/items/', { params });
  },
  
  getItem: (id: number) => api.get(`/items/${id}/`),
  
  createItem: (data: {
    wishlist: number;
    name: string;
    description?: string;
    price: number;
    product_url?: string;
    priority?: number;
  }) => api.post('/items/', data),
  
  updateItem: (id: number, data: any) => api.patch(`/items/${id}/`, data),
  
  deleteItem: (id: number) => api.delete(`/items/${id}/`),
  
  contribute: (id: number, data: {
    amount: number;
    message?: string;
    is_anonymous?: boolean;
  }) => api.post(`/items/${id}/contribute/`, data),
  
  getItemContributors: (id: number) => api.get(`/items/${id}/contributors/`),
};

export const userAPI = {
  getProfile: () => api.get('/users/me/'),
  
  updateProfile: (data: any) => api.patch('/users/me/', data),
  
  getNotifications: () => api.get('/notifications/'),
  
  markNotificationRead: (id: number) =>
    api.post(`/notifications/${id}/mark_read/`),
  
  getTransactions: () => api.get('/transactions/'),
  
  changePassword: (data: { old_password: string; new_password: string }) =>
    api.post('/auth/change-password/', data),
};

export const planAPI = {
  getPlans: () => api.get('/plans/'),
  
  getSubscription: () => api.get('/subscriptions/'),
  
  subscribe: (planId: number) =>
    api.post('/subscriptions/', { plan_id: planId }),
  
  cancelSubscription: (id: number) =>
    api.post(`/subscriptions/${id}/cancel/`),
};

export default api;
