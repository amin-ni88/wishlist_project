import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Alert,
  Share,
  Linking,
  Clipboard,
  SafeAreaView,
} from 'react-native';
import {
  Card,
  Text,
  Button,
  TextInput,
  Chip,
  Switch,
  Portal,
  Dialog,
  Snackbar,
  List,
  Divider,
  FAB,
} from 'react-native-paper';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useRoute } from '@react-navigation/native';

import theme from '../utils/theme';
import ResponsiveLayout from '../components/common/ResponsiveLayout';

const ShareWishlistScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const { wishlistItem } = route.params as any;

  const [shareType, setShareType] = useState('PUBLIC');
  const [allowContributions, setAllowContributions] = useState(true);
  const [allowComments, setAllowComments] = useState(true);
  const [showProgress, setShowProgress] = useState(true);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteMessage, setInviteMessage] = useState('');
  const [suggestedAmount, setSuggestedAmount] = useState('');
  const [shareUrl, setShareUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [inviteDialog, setInviteDialog] = useState(false);
  const [snackbar, setSnackbar] = useState({ visible: false, message: '' });

  const socialPlatforms = [
    { name: 'تلگرام', icon: 'send', color: '#0088cc', id: 'telegram' },
    { name: 'واتساپ', icon: 'logo-whatsapp', color: '#25d366', id: 'whatsapp' },
    { name: 'اینستاگرام', icon: 'logo-instagram', color: '#e4405f', id: 'instagram' },
    { name: 'پیامک', icon: 'chatbubble', color: '#34c759', id: 'sms' },
    { name: 'ایمیل', icon: 'mail', color: '#007aff', id: 'email' },
  ];

  useEffect(() => {
    generateShareUrl();
  }, [shareType, allowContributions, allowComments, showProgress]);

  const generateShareUrl = () => {
    // شبیه‌سازی تولید URL اشتراک‌گذاری
    const baseUrl = 'https://wishlist-app.com/shared';
    const params = new URLSearchParams({
      type: shareType,
      contributions: allowContributions.toString(),
      comments: allowComments.toString(),
      progress: showProgress.toString(),
    });
    setShareUrl(`${baseUrl}/${wishlistItem.id}?${params}`);
  };

  const copyToClipboard = async () => {
    try {
      await Clipboard.setString(shareUrl);
      setSnackbar({ visible: true, message: 'لینک کپی شد!' });
    } catch (error) {
      Alert.alert('خطا', 'امکان کپی لینک وجود ندارد');
    }
  };

  const shareToSocial = async (platform: string) => {
    const shareMessage = `🎁 ${wishlistItem.title}\n\n${wishlistItem.description}\n\nکمک کنید این آرزو محقق شود:\n${shareUrl}`;
    
    try {
      switch (platform) {
        case 'telegram':
          const telegramUrl = `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareMessage)}`;
          await Linking.openURL(telegramUrl);
          break;
          
        case 'whatsapp':
          const whatsappUrl = `whatsapp://send?text=${encodeURIComponent(shareMessage)}`;
          await Linking.openURL(whatsappUrl);
          break;
          
        case 'sms':
          const smsUrl = `sms:?body=${encodeURIComponent(shareMessage)}`;
          await Linking.openURL(smsUrl);
          break;
          
        case 'email':
          const emailUrl = `mailto:?subject=${encodeURIComponent(`کمک به ${wishlistItem.title}`)}&body=${encodeURIComponent(shareMessage)}`;
          await Linking.openURL(emailUrl);
          break;
          
        case 'instagram':
          // برای اینستاگرام می‌توان از Story sharing استفاده کرد
          await Share.share({
            message: shareMessage,
            url: shareUrl,
          });
          break;
          
        default:
          await Share.share({
            message: shareMessage,
            url: shareUrl,
          });
      }
      
      setSnackbar({ visible: true, message: `اشتراک‌گذاری در ${platform} انجام شد` });
    } catch (error) {
      Alert.alert('خطا', 'امکان اشتراک‌گذاری وجود ندارد');
    }
  };

  const sendInvitation = async () => {
    if (!inviteEmail.trim()) {
      Alert.alert('خطا', 'لطفاً ایمیل دوست خود را وارد کنید');
      return;
    }

    setLoading(true);
    try {
      // شبیه‌سازی ارسال دعوت‌نامه
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setInviteDialog(false);
      setInviteEmail('');
      setInviteMessage('');
      setSuggestedAmount('');
      setSnackbar({ visible: true, message: 'دعوت‌نامه ارسال شد!' });
    } catch (error) {
      Alert.alert('خطا', 'خطا در ارسال دعوت‌نامه');
    } finally {
      setLoading(false);
    }
  };

  const getShareTypeText = (type: string) => {
    switch (type) {
      case 'PUBLIC': return 'عمومی - همه می‌توانند ببینند';
      case 'PRIVATE': return 'خصوصی - فقط شما';
      case 'FRIENDS': return 'دوستان - افراد دعوت‌شده';
      case 'LINK': return 'با لینک - کسانی که لینک دارند';
      default: return 'نامشخص';
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient
        colors={[theme.colors.primary, theme.colors.accent]}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <Ionicons name="share-social" size={32} color={theme.colors.white} />
          <Text style={styles.headerTitle}>اشتراک‌گذاری</Text>
          <Text style={styles.headerSubtitle}>{wishlistItem.title}</Text>
        </View>
      </LinearGradient>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <ResponsiveLayout>
          <View style={styles.padding}>

            {/* تنظیمات حریم خصوصی */}
            <Card style={styles.card}>
              <Card.Content>
                <Text style={styles.sectionTitle}>تنظیمات حریم خصوصی</Text>
                
                <View style={styles.radioGroup}>
                  {[
                    { value: 'PUBLIC', label: 'عمومی', desc: 'همه می‌توانند ببینند' },
                    { value: 'FRIENDS', label: 'دوستان', desc: 'فقط افراد دعوت‌شده' },
                    { value: 'LINK', label: 'با لینک', desc: 'کسانی که لینک دارند' },
                  ].map((option) => (
                    <List.Item
                      key={option.value}
                      title={option.label}
                      description={option.desc}
                      left={() => (
                        <View style={styles.radioButton}>
                          <View style={[
                            styles.radioInner,
                            shareType === option.value && styles.radioSelected
                          ]} />
                        </View>
                      )}
                      onPress={() => setShareType(option.value)}
                      style={styles.radioItem}
                    />
                  ))}
                </View>
              </Card.Content>
            </Card>

            {/* تنظیمات اشتراک‌گذاری */}
            <Card style={styles.card}>
              <Card.Content>
                <Text style={styles.sectionTitle}>تنظیمات اشتراک‌گذاری</Text>
                
                <View style={styles.switchRow}>
                  <Text style={styles.switchLabel}>امکان کمک مالی</Text>
                  <Switch
                    value={allowContributions}
                    onValueChange={setAllowContributions}
                  />
                </View>
                
                <View style={styles.switchRow}>
                  <Text style={styles.switchLabel}>امکان نظردهی</Text>
                  <Switch
                    value={allowComments}
                    onValueChange={setAllowComments}
                  />
                </View>
                
                <View style={styles.switchRow}>
                  <Text style={styles.switchLabel}>نمایش پیشرفت</Text>
                  <Switch
                    value={showProgress}
                    onValueChange={setShowProgress}
                  />
                </View>
              </Card.Content>
            </Card>

            {/* لینک اشتراک‌گذاری */}
            <Card style={styles.card}>
              <Card.Content>
                <Text style={styles.sectionTitle}>لینک اشتراک‌گذاری</Text>
                
                <View style={styles.linkContainer}>
                  <TextInput
                    value={shareUrl}
                    editable={false}
                    style={styles.linkInput}
                    right={
                      <TextInput.Icon
                        icon="content-copy"
                        onPress={copyToClipboard}
                      />
                    }
                  />
                </View>
                
                <Text style={styles.linkDescription}>
                  {getShareTypeText(shareType)}
                </Text>
              </Card.Content>
            </Card>

            {/* شبکه‌های اجتماعی */}
            <Card style={styles.card}>
              <Card.Content>
                <Text style={styles.sectionTitle}>اشتراک در شبکه‌های اجتماعی</Text>
                
                <View style={styles.socialGrid}>
                  {socialPlatforms.map((platform) => (
                    <Button
                      key={platform.id}
                      mode="outlined"
                      icon={({ size }) => (
                        <Ionicons
                          name={platform.icon as any}
                          size={size}
                          color={platform.color}
                        />
                      )}
                      onPress={() => shareToSocial(platform.id)}
                      style={[styles.socialButton, { borderColor: platform.color }]}
                      labelStyle={{ color: platform.color }}
                    >
                      {platform.name}
                    </Button>
                  ))}
                </View>
              </Card.Content>
            </Card>

            {/* دعوت دوستان */}
            <Card style={styles.card}>
              <Card.Content>
                <Text style={styles.sectionTitle}>دعوت دوستان</Text>
                <Text style={styles.cardDescription}>
                  دوستان خود را دعوت کنید تا در تحقق آرزوی شما کمک کنند
                </Text>
                
                <Button
                  mode="contained"
                  icon="account-plus"
                  onPress={() => setInviteDialog(true)}
                  style={styles.inviteButton}
                >
                  ارسال دعوت‌نامه
                </Button>
              </Card.Content>
            </Card>

          </View>
        </ResponsiveLayout>
      </ScrollView>

      {/* دیالوگ دعوت */}
      <Portal>
        <Dialog visible={inviteDialog} onDismiss={() => setInviteDialog(false)}>
          <Dialog.Title>دعوت دوست</Dialog.Title>
          <Dialog.Content>
            <TextInput
              label="ایمیل دوست"
              value={inviteEmail}
              onChangeText={setInviteEmail}
              mode="outlined"
              style={styles.dialogInput}
              keyboardType="email-address"
            />
            
            <TextInput
              label="پیام شخصی (اختیاری)"
              value={inviteMessage}
              onChangeText={setInviteMessage}
              mode="outlined"
              multiline
              numberOfLines={3}
              style={styles.dialogInput}
            />
            
            <TextInput
              label="مبلغ پیشنهادی (تومان)"
              value={suggestedAmount}
              onChangeText={setSuggestedAmount}
              mode="outlined"
              keyboardType="numeric"
              style={styles.dialogInput}
            />
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setInviteDialog(false)}>لغو</Button>
            <Button 
              onPress={sendInvitation} 
              mode="contained"
              loading={loading}
            >
              ارسال دعوت
            </Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>

      {/* Snackbar */}
      <Snackbar
        visible={snackbar.visible}
        onDismiss={() => setSnackbar({ visible: false, message: '' })}
        duration={3000}
      >
        {snackbar.message}
      </Snackbar>

      {/* FAB */}
      <FAB
        style={styles.fab}
        icon="share"
        onPress={() => Share.share({
          message: `🎁 ${wishlistItem.title}\n\nکمک کنید این آرزو محقق شود:\n${shareUrl}`,
          url: shareUrl,
        })}
        label="اشتراک سریع"
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    paddingTop: 20,
    paddingBottom: 30,
    paddingHorizontal: 20,
  },
  headerContent: {
    alignItems: 'center',
  },
  headerTitle: {
    ...theme.typography.h2,
    color: theme.colors.white,
    marginTop: 10,
  },
  headerSubtitle: {
    ...theme.typography.body,
    color: theme.colors.white,
    opacity: 0.9,
    marginTop: 5,
    textAlign: 'center',
  },
  content: {
    flex: 1,
    marginTop: -15,
  },
  padding: {
    padding: 16,
  },
  card: {
    marginBottom: 16,
    elevation: 2,
  },
  sectionTitle: {
    ...theme.typography.h4,
    marginBottom: 16,
  },
  cardDescription: {
    ...theme.typography.body2,
    color: theme.colors.grey600,
    marginBottom: 16,
  },
  radioGroup: {
    marginTop: 8,
  },
  radioItem: {
    paddingVertical: 4,
  },
  radioButton: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: theme.colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  radioInner: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  radioSelected: {
    backgroundColor: theme.colors.primary,
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  switchLabel: {
    ...theme.typography.body,
  },
  linkContainer: {
    marginBottom: 8,
  },
  linkInput: {
    marginBottom: 8,
  },
  linkDescription: {
    ...theme.typography.small,
    color: theme.colors.grey600,
  },
  socialGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  socialButton: {
    minWidth: '45%',
    marginBottom: 8,
  },
  inviteButton: {
    marginTop: 8,
  },
  dialogInput: {
    marginBottom: 16,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: theme.colors.primary,
  },
});

export default ShareWishlistScreen; 