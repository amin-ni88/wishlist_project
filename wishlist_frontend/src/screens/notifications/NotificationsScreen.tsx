import React from 'react';
import { StyleSheet, View, FlatList } from 'react-native';
import { List, Text, Card, useTheme, IconButton } from 'react-native-paper';
import { theme } from '../../utils/theme';
import { useRTL, createRTLStyles } from '../../context/RightToLeftContext';

import { Notification } from '../../types/notification';

interface NotificationItemProps {
  notification: Notification;
}

const NotificationItem: React.FC<NotificationItemProps> = ({ notification }) => {
  const getIcon = (type: Notification['type']) => {
    switch (type) {
      case 'CONTRIBUTION':
        return 'hand-heart';
      case 'SUBSCRIPTION':
        return 'crown';
      case 'INVITE':
        return 'account-plus';
      default:
        return 'bell';
    }
  };

  return (
    <Card style={styles.notificationCard}>
      <Card.Content style={styles.notificationContent}>
        <IconButton
          icon={getIcon(notification.type)}
          size={24}
          style={[
            styles.notificationIcon,
            { backgroundColor: notification.read ? theme.colors.secondary : theme.colors.primary },
          ]}
          color={theme.colors.surface}
        />
        <View style={styles.notificationTextContainer}>
          <Text style={styles.notificationTitle}>{notification.title}</Text>
          <Text style={styles.notificationBody}>{notification.body}</Text>
          <Text style={styles.notificationTime}>{notification.time}</Text>
        </View>
      </Card.Content>
    </Card>
  );
};

const NotificationsScreen = () => {
  // Example notifications data
  const notifications = [
    {
      id: '1',
      type: 'CONTRIBUTION',
      title: 'مشارکت جدید',
      body: 'علی در خرید لپ‌تاپ مشارکت کرد',
      time: '۱۰ دقیقه پیش',
      read: false,
    },
    {
      id: '2',
      type: 'SUBSCRIPTION',
      title: 'اشتراک شما',
      body: 'تا ۳ روز دیگر اشتراک شما به پایان می‌رسد',
      time: '۲ ساعت پیش',
      read: true,
    },
    {
      id: '3',
      type: 'INVITE',
      title: 'دعوت به مشارکت',
      body: 'مریم شما را به مشارکت در خرید هدیه دعوت کرد',
      time: 'دیروز',
      read: true,
    },
  ];

  return (
    <View style={styles.container}>
      <FlatList
        data={notifications}
        renderItem={({ item }) => <NotificationItem notification={item} />}
        keyExtractor={item => item.id}
        contentContainerStyle={styles.listContainer}
      />
    </View>
  );
};

const styles = createRTLStyles({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  listContainer: {
    padding: theme.spacing.md,
  },
  notificationCard: {
    marginBottom: theme.spacing.md,
    backgroundColor: theme.colors.surface,
  },
  notificationContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  notificationIcon: {
    marginRight: theme.spacing.md,
  },
  notificationTextContainer: {
    flex: 1,
  },
  notificationTitle: {
    ...theme.typography.h3,
    color: theme.colors.text,
    marginBottom: theme.spacing.xs,
  },
  notificationBody: {
    ...theme.typography.body,
    color: theme.colors.onSurface,
    marginBottom: theme.spacing.xs,
  },
  notificationTime: {
    ...theme.typography.small,
    color: theme.colors.onSurface,
    opacity: 0.7,
  },
});

export default NotificationsScreen;
