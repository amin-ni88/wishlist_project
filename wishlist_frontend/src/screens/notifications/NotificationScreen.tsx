import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  RefreshControl,
  Alert,
} from 'react-native';
import {
  Card,
  Text,
  Button,
  ActivityIndicator,
  Badge,
  Surface,
  IconButton,
  Menu,
  Divider,
} from 'react-native-paper';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { userAPI } from '../../services/api';
import { theme } from '../../utils/theme';

interface NotificationScreenProps {
  navigation: any;
}

interface Notification {
  id: number;
  title: string;
  message: string;
  type: 'CONTRIBUTION' | 'WISHLIST' | 'FOLLOW' | 'GENERAL';
  is_read: boolean;
  created_at: string;
  related_object_id?: number;
}

const NotificationScreen: React.FC<NotificationScreenProps> = ({ navigation }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [menuVisible, setMenuVisible] = useState(false);

  useEffect(() => {
    fetchNotifications();
  }, []);

  useFocusEffect(
    useCallback(() => {
      fetchNotifications();
    }, [])
  );

  const fetchNotifications = async () => {
    try {
      const response = await userAPI.getNotifications();
      setNotifications(response.data.results || []);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchNotifications();
  };

  const markAsRead = async (id: number) => {
    try {
      await userAPI.markNotificationRead(id);
      setNotifications(prev => 
        prev.map(notif => 
          notif.id === id ? { ...notif, is_read: true } : notif
        )
      );
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const unreadNotifications = notifications.filter(n => !n.is_read);
      await Promise.all(
        unreadNotifications.map(notif => userAPI.markNotificationRead(notif.id))
      );
      setNotifications(prev => 
        prev.map(notif => ({ ...notif, is_read: true }))
      );
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      Alert.alert('خطا', 'خطا در علامت‌گذاری اعلان‌ها');
    }
  };

  const deleteAllRead = () => {
    Alert.alert(
      'حذف اعلان‌های خوانده شده',
      'آیا مطمئن هستید که می‌خواهید تمام اعلان‌های خوانده شده را حذف کنید؟',
      [
        { text: 'لغو', style: 'cancel' },
        { 
          text: 'حذف', 
          style: 'destructive', 
          onPress: () => {
            setNotifications(prev => prev.filter(notif => !notif.is_read));
          }
        },
      ]
    );
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'CONTRIBUTION':
        return 'gift';
      case 'WISHLIST':
        return 'list';
      case 'FOLLOW':
        return 'person-add';
      case 'GENERAL':
      default:
        return 'notifications';
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'CONTRIBUTION':
        return theme.colors.secondary;
      case 'WISHLIST':
        return theme.colors.primary;
      case 'FOLLOW':
        return theme.colors.accent;
      case 'GENERAL':
      default:
        return theme.colors.disabled;
    }
  };

  const handleNotificationPress = async (notification: Notification) => {
    if (!notification.is_read) {
      await markAsRead(notification.id);
    }

    // Navigate based on notification type
    switch (notification.type) {
      case 'CONTRIBUTION':
      case 'WISHLIST':
        if (notification.related_object_id) {
          navigation.navigate('ItemDetail', { 
            itemId: notification.related_object_id 
          });
        }
        break;
      case 'FOLLOW':
        navigation.navigate('Profile');
        break;
      default:
        break;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) {
      return 'امروز';
    } else if (diffDays === 2) {
      return 'دیروز';
    } else if (diffDays < 7) {
      return `${diffDays} روز پیش`;
    } else {
      return date.toLocaleDateString('fa-IR');
    }
  };

  const renderNotification = ({ item }: { item: Notification }) => (
    <Card 
      style={[
        styles.notificationCard,
        !item.is_read && styles.unreadCard
      ]}
      onPress={() => handleNotificationPress(item)}
    >
      <Card.Content>
        <View style={styles.notificationHeader}>
          <View style={styles.notificationLeft}>
            <Surface style={[
              styles.iconContainer,
              { backgroundColor: getNotificationColor(item.type) }
            ]}>
              <Ionicons
                name={getNotificationIcon(item.type)}
                size={20}
                color="white"
              />
            </Surface>
            <View style={styles.notificationContent}>
              <Text style={[
                styles.notificationTitle,
                !item.is_read && styles.unreadText
              ]}>
                {item.title}
              </Text>
              <Text style={styles.notificationMessage}>
                {item.message}
              </Text>
              <Text style={styles.notificationDate}>
                {formatDate(item.created_at)}
              </Text>
            </View>
          </View>
          {!item.is_read && (
            <Badge style={styles.unreadBadge} />
          )}
        </View>
      </Card.Content>
    </Card>
  );

  const unreadCount = notifications.filter(n => !n.is_read).length;

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header Actions */}
      {notifications.length > 0 && (
        <Surface style={styles.headerActions}>
          <View style={styles.headerLeft}>
            <Text style={styles.headerText}>
              {unreadCount > 0 ? `${unreadCount} اعلان خوانده نشده` : 'همه اعلان‌ها خوانده شد'}
            </Text>
          </View>
          <View style={styles.headerRight}>
            <Menu
              visible={menuVisible}
              onDismiss={() => setMenuVisible(false)}
              anchor={
                <IconButton
                  icon="dots-vertical"
                  onPress={() => setMenuVisible(true)}
                />
              }
            >
              <Menu.Item
                onPress={() => {
                  setMenuVisible(false);
                  markAllAsRead();
                }}
                title="علامت‌گذاری همه به عنوان خوانده شده"
                leadingIcon="check-all"
              />
              <Divider />
              <Menu.Item
                onPress={() => {
                  setMenuVisible(false);
                  deleteAllRead();
                }}
                title="حذف اعلان‌های خوانده شده"
                leadingIcon="delete"
              />
            </Menu>
          </View>
        </Surface>
      )}

      {/* Notifications List */}
      <FlatList
        data={notifications}
        renderItem={renderNotification}
        keyExtractor={(item) => item.id.toString()}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.listContainer}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons 
              name="notifications-outline" 
              size={64} 
              color={theme.colors.disabled} 
            />
            <Text style={styles.emptyTitle}>هیچ اعلانی وجود ندارد</Text>
            <Text style={styles.emptyMessage}>
              زمانی که اتفاقات جدیدی رخ دهد، اینجا مطلع خواهید شد
            </Text>
          </View>
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    elevation: 2,
  },
  headerLeft: {
    flex: 1,
  },
  headerText: {
    fontSize: 14,
    color: theme.colors.disabled,
  },
  headerRight: {
    flexDirection: 'row',
  },
  listContainer: {
    padding: 16,
  },
  notificationCard: {
    marginBottom: 8,
    elevation: 2,
  },
  unreadCard: {
    borderLeftWidth: 4,
    borderLeftColor: theme.colors.primary,
  },
  notificationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  notificationLeft: {
    flexDirection: 'row',
    flex: 1,
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  notificationContent: {
    flex: 1,
  },
  notificationTitle: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 4,
    color: theme.colors.text,
  },
  unreadText: {
    fontWeight: 'bold',
  },
  notificationMessage: {
    fontSize: 14,
    color: theme.colors.disabled,
    marginBottom: 4,
    lineHeight: 20,
  },
  notificationDate: {
    fontSize: 12,
    color: theme.colors.disabled,
  },
  unreadBadge: {
    backgroundColor: theme.colors.primary,
    marginTop: 4,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 16,
    marginBottom: 8,
    color: theme.colors.text,
  },
  emptyMessage: {
    fontSize: 14,
    color: theme.colors.disabled,
    textAlign: 'center',
    paddingHorizontal: 40,
    lineHeight: 20,
  },
});

export default NotificationScreen; 