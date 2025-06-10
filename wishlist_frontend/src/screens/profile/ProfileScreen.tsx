import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
  Dimensions,
} from 'react-native';
import {
  Avatar,
  Card,
  Title,
  Paragraph,
  Button,
  List,
  Divider,
  Surface,
  Text,
  ActivityIndicator,
} from 'react-native-paper';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../context/AuthContext';
import { userAPI } from '../../services/api';
import { theme } from '../../utils/theme';

const { width } = Dimensions.get('window');

interface ProfileScreenProps {
  navigation: any;
}

const ProfileScreen: React.FC<ProfileScreenProps> = ({ navigation }) => {
  const { user, logout } = useAuth();
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState<any>(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await userAPI.getProfile();
      setProfile(response.data);
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    Alert.alert(
      'خروج از حساب',
      'آیا مطمئن هستید که می‌خواهید خارج شوید؟',
      [
        { text: 'لغو', style: 'cancel' },
        { text: 'خروج', style: 'destructive', onPress: logout },
      ]
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Profile Header */}
      <Surface style={styles.headerCard}>
        <View style={styles.profileHeader}>
          <Avatar.Text
            size={80}
            label={user?.first_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
            style={styles.avatar}
          />
          <View style={styles.profileInfo}>
            <Title style={styles.profileName}>
              {user?.first_name && user?.last_name 
                ? `${user.first_name} ${user.last_name}`
                : user?.username}
            </Title>
            <Paragraph style={styles.profileEmail}>{user?.email}</Paragraph>
            <View style={styles.walletInfo}>
              <Ionicons name="wallet-outline" size={16} color={theme.colors.primary} />
              <Text style={styles.walletText}>
                موجودی: {profile?.wallet_balance || 0} تومان
              </Text>
            </View>
          </View>
        </View>
      </Surface>

      {/* Quick Stats */}
      <View style={styles.statsContainer}>
        <Card style={styles.statCard}>
          <Card.Content style={styles.statContent}>
            <Title style={styles.statNumber}>{profile?.wishlist_count || 0}</Title>
            <Paragraph style={styles.statLabel}>لیست آرزو</Paragraph>
          </Card.Content>
        </Card>
        <Card style={styles.statCard}>
          <Card.Content style={styles.statContent}>
            <Title style={styles.statNumber}>{profile?.followers_count || 0}</Title>
            <Paragraph style={styles.statLabel}>دنبال‌کننده</Paragraph>
          </Card.Content>
        </Card>
        <Card style={styles.statCard}>
          <Card.Content style={styles.statContent}>
            <Title style={styles.statNumber}>{profile?.following_count || 0}</Title>
            <Paragraph style={styles.statLabel}>دنبال‌شده</Paragraph>
          </Card.Content>
        </Card>
      </View>

      {/* Menu Items */}
      <Card style={styles.menuCard}>
        <List.Section>
          <List.Item
            title="کیف پول"
            description="شارژ و تراکنش‌ها"
            left={(props) => <List.Icon {...props} icon="wallet" />}
            right={(props) => <List.Icon {...props} icon="chevron-left" />}
            onPress={() => navigation.navigate('Wallet')}
          />
          <Divider />
          <List.Item
            title="تنظیمات"
            description="حریم خصوصی و امنیت"
            left={(props) => <List.Icon {...props} icon="cog" />}
            right={(props) => <List.Icon {...props} icon="chevron-left" />}
            onPress={() => navigation.navigate('Settings')}
          />
          <Divider />
          <List.Item
            title="دعوت از دوستان"
            description="کسب امتیاز با دعوت"
            left={(props) => <List.Icon {...props} icon="account-plus" />}
            right={(props) => <List.Icon {...props} icon="chevron-left" />}
            onPress={() => {/* Handle invite friends */}}
          />
          <Divider />
          <List.Item
            title="پشتیبانی"
            description="راهنما و تماس با ما"
            left={(props) => <List.Icon {...props} icon="help-circle" />}
            right={(props) => <List.Icon {...props} icon="chevron-left" />}
            onPress={() => {/* Handle support */}}
          />
        </List.Section>
      </Card>

      {/* Logout Button */}
      <Button
        mode="outlined"
        onPress={handleLogout}
        style={styles.logoutButton}
        icon="logout"
      >
        خروج از حساب
      </Button>
    </ScrollView>
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
  headerCard: {
    margin: 16,
    borderRadius: 12,
    elevation: 2,
  },
  profileHeader: {
    flexDirection: 'row',
    padding: 20,
    alignItems: 'center',
  },
  avatar: {
    backgroundColor: theme.colors.primary,
  },
  profileInfo: {
    marginLeft: 16,
    flex: 1,
  },
  profileName: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  profileEmail: {
    color: theme.colors.disabled,
    marginBottom: 8,
  },
  walletInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  walletText: {
    marginLeft: 4,
    color: theme.colors.primary,
    fontWeight: 'bold',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginHorizontal: 16,
    marginBottom: 16,
  },
  statCard: {
    flex: 1,
    marginHorizontal: 4,
    elevation: 2,
  },
  statContent: {
    alignItems: 'center',
    paddingVertical: 12,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.primary,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: theme.colors.disabled,
  },
  menuCard: {
    margin: 16,
    elevation: 2,
  },
  logoutButton: {
    margin: 16,
    borderColor: theme.colors.error,
  },
});

export default ProfileScreen;
