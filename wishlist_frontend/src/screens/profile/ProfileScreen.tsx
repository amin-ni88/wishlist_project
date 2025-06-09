import React from 'react';
import { StyleSheet, View, ScrollView } from 'react-native';
import { Avatar, Text, List, Button, Card } from 'react-native-paper';
import { theme } from '../../utils/theme';

const ProfileScreen = ({ navigation }) => {
  // Example user data
  const user = {
    name: 'کاربر نمونه',
    email: 'user@example.com',
    avatar: null,
    walletBalance: 1500000,
    subscription: {
      plan: 'اشتراک طلایی',
      expiry: '1402/12/29',
    },
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Avatar.Text
          size={80}
          label={user.name.substring(0, 2)}
          style={styles.avatar}
        />
        <Text style={styles.name}>{user.name}</Text>
        <Text style={styles.email}>{user.email}</Text>
      </View>

      <Card style={styles.walletCard}>
        <Card.Content>
          <Text style={styles.walletTitle}>موجودی کیف پول</Text>
          <Text style={styles.walletBalance}>
            {user.walletBalance.toLocaleString()} تومان
          </Text>
          <Button
            mode="contained"
            onPress={() => {}}
            style={styles.chargeButton}
          >
            شارژ کیف پول
          </Button>
        </Card.Content>
      </Card>

      <Card style={styles.subscriptionCard}>
        <Card.Content>
          <Text style={styles.subscriptionTitle}>اشتراک فعال</Text>
          <Text style={styles.subscriptionPlan}>{user.subscription.plan}</Text>
          <Text style={styles.subscriptionExpiry}>
            تاریخ انقضا: {user.subscription.expiry}
          </Text>
          <Button
            mode="outlined"
            onPress={() => {}}
            style={styles.upgradeButton}
          >
            ارتقای اشتراک
          </Button>
        </Card.Content>
      </Card>

      <List.Section>
        <List.Item
          title="آرزوهای من"
          left={props => <List.Icon {...props} icon="gift" />}
          right={props => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => {}}
        />
        <List.Item
          title="مشارکت‌های من"
          left={props => <List.Icon {...props} icon="hand-heart" />}
          right={props => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => {}}
        />
        <List.Item
          title="تنظیمات"
          left={props => <List.Icon {...props} icon="cog" />}
          right={props => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => {}}
        />
        <List.Item
          title="خروج"
          left={props => <List.Icon {...props} icon="logout" color={theme.colors.error} />}
          titleStyle={{ color: theme.colors.error }}
          onPress={() => {}}
        />
      </List.Section>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    alignItems: 'center',
    padding: theme.spacing.xl,
    backgroundColor: theme.colors.primary,
  },
  avatar: {
    backgroundColor: theme.colors.accent,
    marginBottom: theme.spacing.md,
  },
  name: {
    ...theme.typography.h2,
    color: theme.colors.surface,
    marginBottom: theme.spacing.xs,
  },
  email: {
    ...theme.typography.body,
    color: theme.colors.surface,
    opacity: 0.8,
  },
  walletCard: {
    margin: theme.spacing.md,
    backgroundColor: theme.colors.surface,
  },
  walletTitle: {
    ...theme.typography.body,
    color: theme.colors.onSurface,
    marginBottom: theme.spacing.xs,
  },
  walletBalance: {
    ...theme.typography.h2,
    color: theme.colors.accent,
    marginBottom: theme.spacing.md,
  },
  chargeButton: {
    backgroundColor: theme.colors.accent,
  },
  subscriptionCard: {
    margin: theme.spacing.md,
    backgroundColor: theme.colors.surface,
  },
  subscriptionTitle: {
    ...theme.typography.body,
    color: theme.colors.onSurface,
    marginBottom: theme.spacing.xs,
  },
  subscriptionPlan: {
    ...theme.typography.h3,
    color: theme.colors.primary,
    marginBottom: theme.spacing.xs,
  },
  subscriptionExpiry: {
    ...theme.typography.small,
    color: theme.colors.onSurface,
    marginBottom: theme.spacing.md,
  },
  upgradeButton: {
    borderColor: theme.colors.primary,
  },
});

export default ProfileScreen;
