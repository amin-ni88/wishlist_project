import { Platform } from 'react-native';
import PushNotification from 'react-native-push-notification';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axiosConfig from './axiosConfig';

export interface NotificationData {
  id: string;
  title: string;
  body: string;
  data?: any;
  type: 'INVITATION' | 'CONTRIBUTION' | 'PAYMENT' | 'REMINDER' | 'GENERAL';
  isRead: boolean;
  createdAt: string;
}

const notificationService = {
  // تنظیمات اولیه
  configure: () => {
    PushNotification.configure({
      onRegister: function (token) {
        console.log('TOKEN:', token);
        // ارسال توکن به سرور
        notificationService.sendTokenToServer(token.token);
      },

      onNotification: function (notification) {
        console.log('NOTIFICATION:', notification);
        
        // اگر notification کلیک شده، به صفحه مربوطه هدایت کنیم
        if (notification.userInteraction) {
          notificationService.handleNotificationClick(notification);
        }
      },

      onAction: function (notification) {
        console.log('ACTION:', notification.action);
        console.log('NOTIFICATION:', notification);
      },

      onRegistrationError: function (err) {
        console.error(err.message, err);
      },

      permissions: {
        alert: true,
        badge: true,
        sound: true,
      },

      popInitialNotification: true,
      requestPermissions: Platform.OS === 'ios',
    });

    // ایجاد کانال notification برای Android
    if (Platform.OS === 'android') {
      PushNotification.createChannel(
        {
          channelId: 'wishlist-channel',
          channelName: 'Wishlist Notifications',
          channelDescription: 'Notifications for wishlist app',
          soundName: 'default',
          importance: 4,
          vibrate: true,
        },
        (created) => console.log(`Channel created: ${created}`)
      );
    }
  },

  // ارسال توکن به سرور
  sendTokenToServer: async (token: string) => {
    try {
      await axiosConfig.post('/api/notifications/register-device/', {
        token,
        platform: Platform.OS,
      });
    } catch (error) {
      console.error('Failed to send token to server:', error);
    }
  },

  // درخواست permission برای notifications
  requestPermission: async (): Promise<boolean> => {
    try {
      if (Platform.OS === 'ios') {
        const permissions = await PushNotification.requestPermissions();
        return permissions.alert === true;
      }
      return true; // Android معمولاً permission ندارد
    } catch (error) {
      console.error('Failed to request notification permission:', error);
      return false;
    }
  },

  // نمایش notification محلی
  showLocalNotification: (title: string, message: string, data?: any) => {
    PushNotification.localNotification({
      channelId: 'wishlist-channel',
      title,
      message,
      playSound: true,
      soundName: 'default',
      userInfo: data,
    });
  },

  // برنامه‌ریزی notification
  scheduleNotification: (
    title: string,
    message: string,
    date: Date,
    data?: any
  ) => {
    PushNotification.localNotificationSchedule({
      channelId: 'wishlist-channel',
      title,
      message,
      date,
      playSound: true,
      soundName: 'default',
      userInfo: data,
    });
  },

  // لغو notification برنامه‌ریزی شده
  cancelNotification: (id: string) => {
    PushNotification.cancelLocalNotifications({ id });
  },

  // لغو همه notifications
  cancelAllNotifications: () => {
    PushNotification.cancelAllLocalNotifications();
  },

  // دریافت لیست notifications از سرور
  getNotifications: async (): Promise<NotificationData[]> => {
    try {
      const response = await axiosConfig.get('/api/notifications/');
      return response.data.results || response.data;
    } catch (error) {
      console.error('Failed to get notifications:', error);
      return [];
    }
  },

  // علامت‌گذاری notification به عنوان خوانده شده
  markAsRead: async (notificationId: string) => {
    try {
      await axiosConfig.post(`/api/notifications/${notificationId}/mark_read/`);
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  },

  // مدیریت کلیک روی notification
  handleNotificationClick: (notification: any) => {
    const { data } = notification;
    
    if (data && data.type) {
      switch (data.type) {
        case 'INVITATION':
          // هدایت به صفحه دعوت‌نامه
          if (data.invitationToken) {
            // Navigation.navigate('InvitationDetail', { token: data.invitationToken });
          }
          break;
        
        case 'CONTRIBUTION':
          // هدایت به صفحه آیتم
          if (data.itemId) {
            // Navigation.navigate('WishlistItemDetail', { id: data.itemId });
          }
          break;
        
        case 'PAYMENT':
          // هدایت به صفحه پرداخت
          if (data.paymentId) {
            // Navigation.navigate('PaymentDetail', { id: data.paymentId });
          }
          break;
        
        default:
          console.log('Unknown notification type:', data.type);
      }
    }
  },

  // ذخیره notification در storage محلی
  saveNotificationLocally: async (notification: NotificationData) => {
    try {
      const stored = await AsyncStorage.getItem('notifications');
      const notifications = stored ? JSON.parse(stored) : [];
      notifications.unshift(notification);
      
      // نگه داشتن فقط 50 notification آخر
      if (notifications.length > 50) {
        notifications.splice(50);
      }
      
      await AsyncStorage.setItem('notifications', JSON.stringify(notifications));
    } catch (error) {
      console.error('Failed to save notification locally:', error);
    }
  },

  // دریافت notifications محلی
  getLocalNotifications: async (): Promise<NotificationData[]> => {
    try {
      const stored = await AsyncStorage.getItem('notifications');
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Failed to get local notifications:', error);
      return [];
    }
  },

  // حذف notifications محلی
  clearLocalNotifications: async () => {
    try {
      await AsyncStorage.removeItem('notifications');
    } catch (error) {
      console.error('Failed to clear local notifications:', error);
    }
  },

  // دریافت تعداد notifications خوانده نشده
  getUnreadCount: async (): Promise<number> => {
    try {
      const notifications = await notificationService.getNotifications();
      return notifications.filter(n => !n.isRead).length;
    } catch (error) {
      console.error('Failed to get unread count:', error);
      return 0;
    }
  },

  // Notification templates
  templates: {
    invitation: (userName: string, itemName: string) => ({
      title: 'دعوت‌نامه جدید',
      body: `${userName} شما را برای کمک در تهیه "${itemName}" دعوت کرده است`,
    }),
    
    contribution: (contributorName: string, amount: number, itemName: string) => ({
      title: 'کمک مالی جدید',
      body: `${contributorName} مبلغ ${amount.toLocaleString('fa-IR')} تومان برای "${itemName}" کمک کرده است`,
    }),
    
    payment: (status: string, amount: number) => ({
      title: 'وضعیت پرداخت',
      body: `پرداخت ${amount.toLocaleString('fa-IR')} تومان ${status === 'success' ? 'موفق' : 'ناموفق'} بود`,
    }),
    
    reminder: (itemName: string, daysLeft: number) => ({
      title: 'یادآوری',
      body: `${daysLeft} روز تا پایان مهلت تهیه "${itemName}" باقی مانده است`,
    }),
  },
};

export default notificationService; 