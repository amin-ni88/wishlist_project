import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'http://localhost:8000/api'; // Change this to your actual API URL

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to add the auth token
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('token');
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
      // Handle unauthorized access
      await AsyncStorage.multiRemove(['token', 'user']);
      // You might want to trigger a navigation to login screen here
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login/', { email, password });
    return response.data;
  },

  register: async (userData: {
    email: string;
    password: string;
    username: string;
    firstName?: string;
    lastName?: string;
  }) => {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/auth/logout/');
    return response.data;
  },
};

export const wishlistService = {
  getWishlists: async () => {
    const response = await api.get('/wishlists/');
    return response.data;
  },

  getWishlistById: async (id: number) => {
    const response = await api.get(`/wishlists/${id}/`);
    return response.data;
  },

  createWishlist: async (data: {
    title: string;
    description?: string;
    isPrivate: boolean;
  }) => {
    const response = await api.post('/wishlists/', data);
    return response.data;
  },

  updateWishlist: async (id: number, data: {
    title?: string;
    description?: string;
    isPrivate?: boolean;
  }) => {
    const response = await api.patch(`/wishlists/${id}/`, data);
    return response.data;
  },

  deleteWishlist: async (id: number) => {
    const response = await api.delete(`/wishlists/${id}/`);
    return response.data;
  },
};

export const contributionService = {
  contribute: async (wishlistItemId: number, amount: number) => {
    const response = await api.post(`/contributions/`, {
      wishlist_item: wishlistItemId,
      amount,
    });
    return response.data;
  },

  getContributions: async (wishlistItemId: number) => {
    const response = await api.get(`/contributions/${wishlistItemId}/`);
    return response.data;
  },
};

export const notificationService = {
  getNotifications: async () => {
    const response = await api.get('/notifications/');
    return response.data;
  },

  markAsRead: async (notificationId: number) => {
    const response = await api.patch(`/notifications/${notificationId}/read/`);
    return response.data;
  },
};

export default api;
