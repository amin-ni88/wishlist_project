import axiosConfig from './axiosConfig';

export interface ShareSettings {
  shareType: 'PUBLIC' | 'PRIVATE' | 'FRIENDS' | 'LINK';
  allowContributions: boolean;
  allowComments: boolean;
  showProgress: boolean;
  expiresInDays?: number;
}

export interface InvitationData {
  wishlistItemId: number;
  invitedEmail?: string;
  invitedPhone?: string;
  invitedName?: string;
  message: string;
  suggestedAmount?: number;
}

export interface SocialShareData {
  wishlistItemId: number;
  platform: 'TELEGRAM' | 'WHATSAPP' | 'INSTAGRAM' | 'SMS' | 'EMAIL';
  shareContent: string;
}

const sharingService = {
  // ایجاد لینک اشتراک‌گذاری
  createShareLink: async (wishlistId: number, settings: ShareSettings) => {
    const response = await axiosConfig.post('/api/create-share-link/', {
      wishlist_id: wishlistId,
      share_type: settings.shareType,
      allow_contributions: settings.allowContributions,
      allow_comments: settings.allowComments,
      show_progress: settings.showProgress,
      expires_in_days: settings.expiresInDays,
    });
    return response.data;
  },

  // دریافت لیست اشتراک‌گذاری‌های کاربر
  getUserShares: async () => {
    const response = await axiosConfig.get('/api/shares/');
    return response.data;
  },

  // حذف اشتراک‌گذاری
  deleteShare: async (shareId: number) => {
    const response = await axiosConfig.delete(`/api/shares/${shareId}/`);
    return response.data;
  },

  // ارسال دعوت‌نامه
  sendInvitation: async (invitationData: InvitationData) => {
    const response = await axiosConfig.post('/api/invitations/', {
      wishlist_item: invitationData.wishlistItemId,
      invited_email: invitationData.invitedEmail,
      invited_phone: invitationData.invitedPhone,
      invited_name: invitationData.invitedName,
      message: invitationData.message,
      suggested_amount: invitationData.suggestedAmount,
    });
    return response.data;
  },

  // دریافت لیست دعوت‌نامه‌های ارسالی
  getSentInvitations: async () => {
    const response = await axiosConfig.get('/api/invitations/');
    return response.data;
  },

  // دریافت جزئیات دعوت‌نامه با توکن
  getInvitationDetails: async (token: string) => {
    const response = await axiosConfig.get(`/api/invitations/details/?token=${token}`);
    return response.data;
  },

  // پذیرش دعوت‌نامه
  acceptInvitation: async (token: string) => {
    const response = await axiosConfig.get(`/api/invitations/accept_invitation/?token=${token}`);
    return response.data;
  },

  // رد دعوت‌نامه
  declineInvitation: async (token: string, message?: string) => {
    const response = await axiosConfig.post('/api/invitations/decline_invitation/', {
      token,
      message,
    });
    return response.data;
  },

  // ثبت اشتراک‌گذاری در شبکه اجتماعی
  recordSocialShare: async (shareData: SocialShareData) => {
    const response = await axiosConfig.post('/api/social-shares/', {
      wishlist_item: shareData.wishlistItemId,
      platform: shareData.platform,
      share_content: shareData.shareContent,
    });
    return response.data;
  },

  // ثبت کلیک روی لینک اشتراک‌گذاری
  trackShareClick: async (shareId: number) => {
    const response = await axiosConfig.post(`/api/social-shares/${shareId}/track_click/`);
    return response.data;
  },

  // ثبت تبدیل (کمک مالی ناشی از اشتراک)
  trackShareConversion: async (shareId: number) => {
    const response = await axiosConfig.post(`/api/social-shares/${shareId}/track_conversion/`);
    return response.data;
  },

  // دریافت لیست آرزوی اشتراک‌گذاری شده
  getSharedWishlist: async (shareToken: string) => {
    const response = await axiosConfig.get(`/api/shared/${shareToken}/`);
    return response.data;
  },

  // افزایش تعداد بازدید
  incrementShareView: async (shareId: number) => {
    const response = await axiosConfig.post(`/api/shares/${shareId}/increment_view/`);
    return response.data;
  },

  // تولید متن اشتراک‌گذاری
  generateShareText: (itemName: string, itemPrice: number, shareUrl: string, userName: string) => {
    return `🎁 ${userName} شما را برای کمک در تهیه "${itemName}" دعوت می‌کند!
    
💰 قیمت: ${itemPrice.toLocaleString('fa-IR')} تومان

🔗 برای مشاهده و کمک کردن روی لینک زیر کلیک کنید:
${shareUrl}

#لیست_آرزو #کمک_مالی #هدیه`;
  },

  // تولید لینک‌های مختلف شبکه‌های اجتماعی
  generateSocialLinks: (shareText: string, shareUrl: string) => {
    const encodedText = encodeURIComponent(shareText);
    const encodedUrl = encodeURIComponent(shareUrl);
    
    return {
      telegram: `https://t.me/share/url?url=${encodedUrl}&text=${encodedText}`,
      whatsapp: `https://wa.me/?text=${encodedText}%20${encodedUrl}`,
      twitter: `https://twitter.com/intent/tweet?text=${encodedText}&url=${encodedUrl}`,
      sms: `sms:?body=${encodedText}%20${encodedUrl}`,
      email: `mailto:?subject=دعوت به کمک&body=${encodedText}%20${encodedUrl}`,
    };
  },

  // کپی کردن متن در کلیپ‌بورد
  copyToClipboard: async (text: string): Promise<boolean> => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return true;
      } else {
        // Fallback برای مرورگرهای قدیمی
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        const success = document.execCommand('copy');
        textArea.remove();
        return success;
      }
    } catch (error) {
      console.error('Failed to copy text:', error);
      return false;
    }
  },

  // Validation برای ایمیل
  validateEmail: (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  // Validation برای شماره تلفن ایران
  validatePhoneNumber: (phone: string): boolean => {
    const phoneRegex = /^(\+98|0)?9[0-9]{9}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
  },

  // فرمت کردن شماره تلفن
  formatPhoneNumber: (phone: string): string => {
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.startsWith('98')) {
      return '+' + cleaned;
    } else if (cleaned.startsWith('0')) {
      return '+98' + cleaned.substring(1);
    } else if (cleaned.length === 10) {
      return '+98' + cleaned;
    }
    return phone;
  },
};

export default sharingService; 