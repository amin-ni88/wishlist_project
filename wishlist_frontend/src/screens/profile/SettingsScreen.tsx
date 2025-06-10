import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
  Linking,
} from 'react-native';
import {
  List,
  Switch,
  Card,
  Title,
  Text,
  Button,
  Divider,
  Portal,
  Modal,
  TextInput,
  ActivityIndicator,
} from 'react-native-paper';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../context/AuthContext';
import { userAPI } from '../../services/api';
import { theme } from '../../utils/theme';

interface SettingsScreenProps {
  navigation: any;
}

interface UserSettings {
  email_notifications: boolean;
  push_notifications: boolean;
  privacy_public_profile: boolean;
  privacy_show_contributions: boolean;
  theme_dark_mode: boolean;
}

const SettingsScreen: React.FC<SettingsScreenProps> = ({ navigation }) => {
  const { user, logout } = useAuth();
  const [settings, setSettings] = useState<UserSettings>({
    email_notifications: true,
    push_notifications: true,
    privacy_public_profile: false,
    privacy_show_contributions: true,
    theme_dark_mode: false,
  });
  const [loading, setLoading] = useState(false);
  const [changePasswordVisible, setChangePasswordVisible] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await userAPI.getProfile();
      const userSettings = response.data.settings || {};
      setSettings({
        email_notifications: userSettings.email_notifications ?? true,
        push_notifications: userSettings.push_notifications ?? true,
        privacy_public_profile: userSettings.privacy_public_profile ?? false,
        privacy_show_contributions: userSettings.privacy_show_contributions ?? true,
        theme_dark_mode: userSettings.theme_dark_mode ?? false,
      });
    } catch (error) {
      console.error('Error fetching settings:', error);
    }
  };

  const updateSetting = async (key: keyof UserSettings, value: boolean) => {
    try {
      setSettings(prev => ({ ...prev, [key]: value }));
      await userAPI.updateProfile({ 
        settings: { ...settings, [key]: value } 
      });
    } catch (error) {
      console.error('Error updating setting:', error);
      // Revert on error
      setSettings(prev => ({ ...prev, [key]: !value }));
      Alert.alert('خطا', 'تغییرات ذخیره نشد. لطفا دوباره تلاش کنید.');
    }
  };

  const handleChangePassword = async () => {
    if (!passwordData.currentPassword || !passwordData.newPassword) {
      Alert.alert('خطا', 'لطفا تمام فیلدها را پر کنید');
      return;
    }

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      Alert.alert('خطا', 'رمز عبور جدید و تکرار آن یکسان نیستند');
      return;
    }

    if (passwordData.newPassword.length < 6) {
      Alert.alert('خطا', 'رمز عبور باید حداقل ۶ کاراکتر باشد');
      return;
    }

    try {
      setLoading(true);
      // Call change password API
      await userAPI.changePassword({
        old_password: passwordData.currentPassword,
        new_password: passwordData.newPassword,
      });
      
      Alert.alert('موفقیت', 'رمز عبور با موفقیت تغییر کرد');
      setChangePasswordVisible(false);
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    } catch (error: any) {
      Alert.alert('خطا', error.response?.data?.detail || 'خطا در تغییر رمز عبور');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = () => {
    Alert.alert(
      'حذف حساب کاربری',
      'آیا مطمئن هستید که می‌خواهید حساب کاربری خود را حذف کنید؟ این عمل غیرقابل بازگشت است.',
      [
        { text: 'لغو', style: 'cancel' },
        { 
          text: 'حذف', 
          style: 'destructive', 
          onPress: () => {
            Alert.alert('در حال توسعه', 'این قابلیت به زودی اضافه خواهد شد.');
          }
        },
      ]
    );
  };

  const openUrl = (url: string) => {
    Linking.openURL(url).catch(() => {
      Alert.alert('خطا', 'امکان باز کردن لینک وجود ندارد');
    });
  };

  return (
    <ScrollView style={styles.container}>
      {/* Notifications */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.sectionTitle}>اعلان‌ها</Title>
          <List.Section>
            <List.Item
              title="اعلان‌های ایمیل"
              description="دریافت اعلان‌ها از طریق ایمیل"
              left={(props) => <List.Icon {...props} icon="email" />}
              right={() => (
                <Switch
                  value={settings.email_notifications}
                  onValueChange={(value) => updateSetting('email_notifications', value)}
                />
              )}
            />
            <List.Item
              title="اعلان‌های push"
              description="دریافت اعلان‌ها در اپلیکیشن"
              left={(props) => <List.Icon {...props} icon="bell" />}
              right={() => (
                <Switch
                  value={settings.push_notifications}
                  onValueChange={(value) => updateSetting('push_notifications', value)}
                />
              )}
            />
          </List.Section>
        </Card.Content>
      </Card>

      {/* Privacy */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.sectionTitle}>حریم خصوصی</Title>
          <List.Section>
            <List.Item
              title="پروفایل عمومی"
              description="سایر کاربران بتوانند پروفایل شما را ببینند"
              left={(props) => <List.Icon {...props} icon="account" />}
              right={() => (
                <Switch
                  value={settings.privacy_public_profile}
                  onValueChange={(value) => updateSetting('privacy_public_profile', value)}
                />
              )}
            />
            <List.Item
              title="نمایش مشارکت‌ها"
              description="سایر کاربران مشارکت‌های شما را ببینند"
              left={(props) => <List.Icon {...props} icon="gift" />}
              right={() => (
                <Switch
                  value={settings.privacy_show_contributions}
                  onValueChange={(value) => updateSetting('privacy_show_contributions', value)}
                />
              )}
            />
          </List.Section>
        </Card.Content>
      </Card>

      {/* Security */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.sectionTitle}>امنیت</Title>
          <List.Section>
            <List.Item
              title="تغییر رمز عبور"
              description="رمز عبور جدید تنظیم کنید"
              left={(props) => <List.Icon {...props} icon="lock" />}
              right={(props) => <List.Icon {...props} icon="chevron-left" />}
              onPress={() => setChangePasswordVisible(true)}
            />
            <List.Item
              title="خروج از تمام دستگاه‌ها"
              description="از تمام دستگاه‌های متصل خارج شوید"
              left={(props) => <List.Icon {...props} icon="devices" />}
              right={(props) => <List.Icon {...props} icon="chevron-left" />}
              onPress={() => {
                Alert.alert('در حال توسعه', 'این قابلیت به زودی اضافه خواهد شد.');
              }}
            />
          </List.Section>
        </Card.Content>
      </Card>

      {/* App Info */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.sectionTitle}>درباره اپلیکیشن</Title>
          <List.Section>
            <List.Item
              title="قوانین و مقررات"
              left={(props) => <List.Icon {...props} icon="file-document" />}
              right={(props) => <List.Icon {...props} icon="chevron-left" />}
              onPress={() => openUrl('https://example.com/terms')}
            />
            <List.Item
              title="حریم خصوصی"
              left={(props) => <List.Icon {...props} icon="shield" />}
              right={(props) => <List.Icon {...props} icon="chevron-left" />}
              onPress={() => openUrl('https://example.com/privacy')}
            />
            <List.Item
              title="تماس با ما"
              left={(props) => <List.Icon {...props} icon="phone" />}
              right={(props) => <List.Icon {...props} icon="chevron-left" />}
              onPress={() => openUrl('mailto:support@example.com')}
            />
            <List.Item
              title="نسخه"
              description="1.0.0"
              left={(props) => <List.Icon {...props} icon="information" />}
            />
          </List.Section>
        </Card.Content>
      </Card>

      {/* Danger Zone */}
      <Card style={styles.dangerCard}>
        <Card.Content>
          <Title style={styles.dangerTitle}>منطقه خطر</Title>
          <Button
            mode="outlined"
            onPress={handleDeleteAccount}
            style={styles.dangerButton}
            textColor={theme.colors.error}
            icon="delete"
          >
            حذف حساب کاربری
          </Button>
        </Card.Content>
      </Card>

      {/* Change Password Modal */}
      <Portal>
        <Modal
          visible={changePasswordVisible}
          onDismiss={() => setChangePasswordVisible(false)}
          contentContainerStyle={styles.modal}
        >
          <Title style={styles.modalTitle}>تغییر رمز عبور</Title>
          
          <TextInput
            label="رمز عبور فعلی"
            value={passwordData.currentPassword}
            onChangeText={(text) => setPasswordData(prev => ({ ...prev, currentPassword: text }))}
            secureTextEntry
            mode="outlined"
            style={styles.modalInput}
          />
          
          <TextInput
            label="رمز عبور جدید"
            value={passwordData.newPassword}
            onChangeText={(text) => setPasswordData(prev => ({ ...prev, newPassword: text }))}
            secureTextEntry
            mode="outlined"
            style={styles.modalInput}
          />
          
          <TextInput
            label="تکرار رمز عبور جدید"
            value={passwordData.confirmPassword}
            onChangeText={(text) => setPasswordData(prev => ({ ...prev, confirmPassword: text }))}
            secureTextEntry
            mode="outlined"
            style={styles.modalInput}
          />
          
          <View style={styles.modalButtons}>
            <Button
              mode="outlined"
              onPress={() => setChangePasswordVisible(false)}
              style={styles.modalButton}
              disabled={loading}
            >
              لغو
            </Button>
            <Button
              mode="contained"
              onPress={handleChangePassword}
              style={styles.modalButton}
              disabled={loading}
            >
              {loading ? <ActivityIndicator size="small" color="white" /> : 'تغییر'}
            </Button>
          </View>
        </Modal>
      </Portal>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  card: {
    margin: 16,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
    color: theme.colors.text,
  },
  dangerCard: {
    margin: 16,
    marginBottom: 32,
    elevation: 2,
    borderColor: theme.colors.error,
    borderWidth: 1,
  },
  dangerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
    color: theme.colors.error,
  },
  dangerButton: {
    borderColor: theme.colors.error,
  },
  modal: {
    backgroundColor: theme.colors.surface,
    padding: 20,
    margin: 20,
    borderRadius: 12,
  },
  modalTitle: {
    textAlign: 'center',
    marginBottom: 20,
  },
  modalInput: {
    marginBottom: 16,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
  },
  modalButton: {
    flex: 1,
    marginHorizontal: 8,
  },
});

export default SettingsScreen; 