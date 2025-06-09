import { useState, useCallback } from 'react';
import { wishlistService, contributionService } from '../services/api';

export const useWishlist = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [wishlists, setWishlists] = useState([]);

  const fetchWishlists = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await wishlistService.getWishlists();
      setWishlists(response);
      return response;
    } catch (err) {
      setError(err.response?.data?.message || 'خطا در دریافت لیست آرزوها');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getWishlistById = useCallback(async (id: number) => {
    try {
      setLoading(true);
      setError(null);
      const response = await wishlistService.getWishlistById(id);
      return response;
    } catch (err) {
      setError(err.response?.data?.message || 'خطا در دریافت جزئیات لیست آرزو');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const createWishlist = useCallback(async (data: {
    title: string;
    description?: string;
    isPrivate: boolean;
  }) => {
    try {
      setLoading(true);
      setError(null);
      const response = await wishlistService.createWishlist(data);
      setWishlists(prev => [...prev, response]);
      return response;
    } catch (err) {
      setError(err.response?.data?.message || 'خطا در ایجاد لیست آرزو');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateWishlist = useCallback(async (id: number, data: {
    title?: string;
    description?: string;
    isPrivate?: boolean;
  }) => {
    try {
      setLoading(true);
      setError(null);
      const response = await wishlistService.updateWishlist(id, data);
      setWishlists(prev => 
        prev.map(w => w.id === id ? { ...w, ...response } : w)
      );
      return response;
    } catch (err) {
      setError(err.response?.data?.message || 'خطا در به‌روزرسانی لیست آرزو');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteWishlist = useCallback(async (id: number) => {
    try {
      setLoading(true);
      setError(null);
      await wishlistService.deleteWishlist(id);
      setWishlists(prev => prev.filter(w => w.id !== id));
    } catch (err) {
      setError(err.response?.data?.message || 'خطا در حذف لیست آرزو');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const contribute = useCallback(async (wishlistItemId: number, amount: number) => {
    try {
      setLoading(true);
      setError(null);
      const response = await contributionService.contribute(wishlistItemId, amount);
      return response;
    } catch (err) {
      setError(err.response?.data?.message || 'خطا در ثبت مشارکت');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    wishlists,
    loading,
    error,
    fetchWishlists,
    getWishlistById,
    createWishlist,
    updateWishlist,
    deleteWishlist,
    contribute,
  };
};
