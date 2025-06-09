import { useState, useCallback, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { authService } from '../services/api';

export const useAuth = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user, setUser } = useContext(AuthContext);

  const login = useCallback(async (email: string, password: string) => {
    try {
      setLoading(true);
      setError(null);
      const response = await authService.login(email, password);
      setUser(response.user);
      return response;
    } catch (err) {
      setError(err.response?.data?.message || 'خطا در ورود به سیستم');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [setUser]);

  const register = useCallback(async (userData: {
    email: string;
    password: string;
    username: string;
    firstName?: string;
    lastName?: string;
  }) => {
    try {
      setLoading(true);
      setError(null);
      const response = await authService.register(userData);
      setUser(response.user);
      return response;
    } catch (err) {
      setError(err.response?.data?.message || 'خطا در ثبت‌نام');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [setUser]);

  const logout = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      await authService.logout();
      setUser(null);
    } catch (err) {
      setError(err.response?.data?.message || 'خطا در خروج از سیستم');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [setUser]);

  return {
    user,
    loading,
    error,
    login,
    register,
    logout,
  };
};
