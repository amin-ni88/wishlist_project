// Payment Service for Zarinpal Integration
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface PaymentRequest {
  amount: number;
  description: string;
  callback_url?: string;
  mobile?: string;
  email?: string;
  order_id?: string;
}

export interface PaymentResponse {
  status: number;
  authority: string;
  message?: string;
}

export interface PaymentVerification {
  status: number;
  ref_id?: string;
  message?: string;
  amount?: number;
}

const ZARINPAL_CONFIG = {
  MERCHANT_ID: 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX', // باید از Zarinpal دریافت شود
  SANDBOX_URL: 'https://www.zarinpal.com/pg/services/WebGate/wsdl',
  PRODUCTION_URL: 'https://www.zarinpal.com/pg/services/WebGate/wsdl',
  PAYMENT_URL: 'https://www.zarinpal.com/pg/StartPay/',
  SANDBOX_PAYMENT_URL: 'https://sandbox.zarinpal.com/pg/StartPay/',
  IS_SANDBOX: true, // در حالت تولید به false تغییر دهید
};

class PaymentService {
  private baseUrl: string;
  private paymentUrl: string;

  constructor() {
    this.baseUrl = ZARINPAL_CONFIG.IS_SANDBOX 
      ? ZARINPAL_CONFIG.SANDBOX_URL 
      : ZARINPAL_CONFIG.PRODUCTION_URL;
    
    this.paymentUrl = ZARINPAL_CONFIG.IS_SANDBOX 
      ? ZARINPAL_CONFIG.SANDBOX_PAYMENT_URL 
      : ZARINPAL_CONFIG.PAYMENT_URL;
  }

  // درخواست پرداخت
  async requestPayment(paymentData: PaymentRequest): Promise<PaymentResponse> {
    try {
      const token = await AsyncStorage.getItem('token');
      
      const response = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/api/payment/request/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...paymentData,
          merchant_id: ZARINPAL_CONFIG.MERCHANT_ID,
        }),
      });

      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.message || 'خطا در درخواست پرداخت');
      }

      return result;
    } catch (error) {
      console.error('Payment request error:', error);
      throw error;
    }
  }

  // تایید پرداخت
  async verifyPayment(authority: string, amount: number): Promise<PaymentVerification> {
    try {
      const token = await AsyncStorage.getItem('token');
      
      const response = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/api/payment/verify/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          authority,
          amount,
          merchant_id: ZARINPAL_CONFIG.MERCHANT_ID,
        }),
      });

      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.message || 'خطا در تایید پرداخت');
      }

      return result;
    } catch (error) {
      console.error('Payment verification error:', error);
      throw error;
    }
  }

  // ساخت URL پرداخت
  getPaymentUrl(authority: string): string {
    return `${this.paymentUrl}${authority}`;
  }

  // بررسی وضعیت پرداخت
  async getPaymentStatus(transactionId: string): Promise<any> {
    try {
      const token = await AsyncStorage.getItem('token');
      
      const response = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/api/payment/status/${transactionId}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.message || 'خطا در دریافت وضعیت پرداخت');
      }

      return result;
    } catch (error) {
      console.error('Payment status error:', error);
      throw error;
    }
  }

  // دریافت تاریخچه پرداخت‌ها
  async getPaymentHistory(page: number = 1, limit: number = 10): Promise<any> {
    try {
      const token = await AsyncStorage.getItem('token');
      
      const response = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/api/payment/history/?page=${page}&limit=${limit}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.message || 'خطا در دریافت تاریخچه پرداخت‌ها');
      }

      return result;
    } catch (error) {
      console.error('Payment history error:', error);
      throw error;
    }
  }

  // پرداخت برای کمک به آیتم لیست آرزو
  async contributeToWishlistItem(itemId: string, amount: number, isAnonymous: boolean = false): Promise<PaymentResponse> {
    const paymentData: PaymentRequest = {
      amount: amount * 10, // تبدیل به ریال (تومان × 10)
      description: `کمک به آیتم لیست آرزو - ${itemId}`,
      order_id: `wishlist_${itemId}_${Date.now()}`,
      callback_url: `${process.env.EXPO_PUBLIC_API_URL}/api/payment/callback/`,
    };

    return this.requestPayment(paymentData);
  }

  // شارژ کیف پول
  async chargeWallet(amount: number): Promise<PaymentResponse> {
    const paymentData: PaymentRequest = {
      amount: amount * 10, // تبدیل به ریال
      description: `شارژ کیف پول`,
      order_id: `wallet_charge_${Date.now()}`,
      callback_url: `${process.env.EXPO_PUBLIC_API_URL}/api/payment/callback/`,
    };

    return this.requestPayment(paymentData);
  }

  // فرمت کردن مبلغ
  formatAmount(amount: number): string {
    return new Intl.NumberFormat('fa-IR').format(amount);
  }

  // تبدیل تومان به ریال
  tomanToRial(toman: number): number {
    return toman * 10;
  }

  // تبدیل ریال به تومان
  rialToToman(rial: number): number {
    return rial / 10;
  }
}

export default new PaymentService(); 