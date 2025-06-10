import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
  TouchableOpacity,
  Image,
  TextInput,
} from 'react-native';
import { useRoute, useNavigation, RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { colors, typography, spacing } from '../theme';
import sharingService from '../services/sharingService';
import { RootStackParamList } from '../navigation/AppNavigator';

type InvitationScreenRouteProp = RouteProp<RootStackParamList, 'Invitation'>;
type InvitationScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Invitation'>;

interface InvitationData {
  id: string;
  wishlistItem: {
    id: number;
    name: string;
    description: string;
    price: number;
    image?: string;
  };
  invitedBy: {
    name: string;
    avatar?: string;
  };
  message: string;
  suggestedAmount?: number;
  status: 'PENDING' | 'ACCEPTED' | 'DECLINED' | 'EXPIRED';
}

const InvitationScreen: React.FC = () => {
  const route = useRoute<InvitationScreenRouteProp>();
  const navigation = useNavigation<InvitationScreenNavigationProp>();
  const { token } = route.params;

  const [loading, setLoading] = useState(true);
  const [invitation, setInvitation] = useState<InvitationData | null>(null);
  const [responseMessage, setResponseMessage] = useState('');
  const [responding, setResponding] = useState(false);

  useEffect(() => {
    loadInvitationDetails();
  }, [token]);

  const loadInvitationDetails = async () => {
    try {
      setLoading(true);
      const response = await sharingService.getInvitationDetails(token);
      setInvitation(response);
    } catch (error) {
      console.error('Failed to load invitation:', error);
      Alert.alert(
        'خطا',
        'دعوت‌نامه یافت نشد یا منقضی شده است',
        [{ text: 'بازگشت', onPress: () => navigation.goBack() }]
      );
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async () => {
    try {
      setResponding(true);
      await sharingService.acceptInvitation(token);
      
      Alert.alert(
        'موفق',
        'دعوت‌نامه پذیرفته شد! حالا می‌توانید در تحقق این آرزو کمک کنید',
        [
          {
            text: 'مشاهده آیتم',
            onPress: () => navigation.navigate('WishlistItemDetail', { 
              id: invitation?.wishlistItem.id 
            })
          }
        ]
      );
    } catch (error) {
      console.error('Failed to accept invitation:', error);
      Alert.alert('خطا', 'خطا در پذیرش دعوت‌نامه');
    } finally {
      setResponding(false);
    }
  };

  const handleDecline = async () => {
    try {
      setResponding(true);
      await sharingService.declineInvitation(token, responseMessage);
      
      Alert.alert(
        'انجام شد',
        'دعوت‌نامه رد شد',
        [{ text: 'بازگشت', onPress: () => navigation.goBack() }]
      );
    } catch (error) {
      console.error('Failed to decline invitation:', error);
      Alert.alert('خطا', 'خطا در رد دعوت‌نامه');
    } finally {
      setResponding(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>در حال بارگذاری...</Text>
      </View>
    );
  }

  if (!invitation) {
    return (
      <View style={styles.errorContainer}>
        <Icon name="error-outline" size={64} color={colors.error} />
        <Text style={styles.errorText}>دعوت‌نامه یافت نشد</Text>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Text style={styles.backButtonText}>بازگشت</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (invitation.status !== 'PENDING') {
    const statusText = {
      ACCEPTED: 'این دعوت‌نامه قبلاً پذیرفته شده است',
      DECLINED: 'این دعوت‌نامه قبلاً رد شده است',
      EXPIRED: 'این دعوت‌نامه منقضی شده است',
    };

    return (
      <View style={styles.statusContainer}>
        <Icon 
          name={invitation.status === 'ACCEPTED' ? 'check-circle' : 'cancel'} 
          size={64} 
          color={invitation.status === 'ACCEPTED' ? colors.success : colors.error} 
        />
        <Text style={styles.statusText}>{statusText[invitation.status]}</Text>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Text style={styles.backButtonText}>بازگشت</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      <LinearGradient
        colors={[colors.primary, colors.secondary]}
        style={styles.header}
      >
        <TouchableOpacity 
          style={styles.backIcon}
          onPress={() => navigation.goBack()}
        >
          <Icon name="arrow-back" size={24} color="white" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>دعوت‌نامه</Text>
      </LinearGradient>

      <View style={styles.inviterSection}>
        <View style={styles.avatarContainer}>
          {invitation.invitedBy.avatar ? (
            <Image source={{ uri: invitation.invitedBy.avatar }} style={styles.avatar} />
          ) : (
            <View style={styles.avatarPlaceholder}>
              <Icon name="person" size={32} color={colors.textSecondary} />
            </View>
          )}
        </View>
        <Text style={styles.inviterName}>{invitation.invitedBy.name}</Text>
        <Text style={styles.inviteText}>شما را دعوت کرده تا در تحقق آرزویش کمک کنید</Text>
      </View>

      <View style={styles.itemSection}>
        <View style={styles.itemCard}>
          {invitation.wishlistItem.image && (
            <Image 
              source={{ uri: invitation.wishlistItem.image }} 
              style={styles.itemImage} 
            />
          )}
          <View style={styles.itemInfo}>
            <Text style={styles.itemName}>{invitation.wishlistItem.name}</Text>
            <Text style={styles.itemDescription}>{invitation.wishlistItem.description}</Text>
            <View style={styles.priceContainer}>
              <Icon name="attach-money" size={20} color={colors.success} />
              <Text style={styles.itemPrice}>
                {invitation.wishlistItem.price.toLocaleString('fa-IR')} تومان
              </Text>
            </View>
            {invitation.suggestedAmount && (
              <View style={styles.suggestedAmountContainer}>
                <Text style={styles.suggestedAmountLabel}>مبلغ پیشنهادی:</Text>
                <Text style={styles.suggestedAmount}>
                  {invitation.suggestedAmount.toLocaleString('fa-IR')} تومان
                </Text>
              </View>
            )}
          </View>
        </View>
      </View>

      {invitation.message && (
        <View style={styles.messageSection}>
          <Text style={styles.messageTitle}>پیام:</Text>
          <Text style={styles.messageText}>{invitation.message}</Text>
        </View>
      )}

      <View style={styles.responseSection}>
        <Text style={styles.responseTitle}>پاسخ شما:</Text>
        <TextInput
          style={styles.responseInput}
          placeholder="پیام اختیاری..."
          placeholderTextColor={colors.textSecondary}
          value={responseMessage}
          onChangeText={setResponseMessage}
          multiline
          maxLength={200}
        />
      </View>

      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={[styles.actionButton, styles.acceptButton]}
          onPress={handleAccept}
          disabled={responding}
        >
          {responding ? (
            <ActivityIndicator size="small" color="white" />
          ) : (
            <>
              <Icon name="check" size={20} color="white" />
              <Text style={styles.buttonText}>پذیرش و کمک</Text>
            </>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.actionButton, styles.declineButton]}
          onPress={handleDecline}
          disabled={responding}
        >
          {responding ? (
            <ActivityIndicator size="small" color="white" />
          ) : (
            <>
              <Icon name="close" size={20} color="white" />
              <Text style={styles.buttonText}>رد کردن</Text>
            </>
          )}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  contentContainer: {
    paddingBottom: spacing.large,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  loadingText: {
    ...typography.body,
    marginTop: spacing.medium,
    color: colors.textSecondary,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
    padding: spacing.large,
  },
  errorText: {
    ...typography.h3,
    color: colors.error,
    marginTop: spacing.medium,
    textAlign: 'center',
  },
  statusContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
    padding: spacing.large,
  },
  statusText: {
    ...typography.h3,
    color: colors.textPrimary,
    marginTop: spacing.medium,
    textAlign: 'center',
  },
  header: {
    paddingTop: 50,
    paddingBottom: spacing.large,
    paddingHorizontal: spacing.medium,
    flexDirection: 'row',
    alignItems: 'center',
  },
  backIcon: {
    padding: spacing.small,
  },
  headerTitle: {
    ...typography.h2,
    color: 'white',
    marginLeft: spacing.medium,
  },
  inviterSection: {
    alignItems: 'center',
    padding: spacing.large,
    backgroundColor: 'white',
    marginTop: -20,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  avatarContainer: {
    marginBottom: spacing.medium,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
  },
  avatarPlaceholder: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.surface,
    justifyContent: 'center',
    alignItems: 'center',
  },
  inviterName: {
    ...typography.h3,
    color: colors.textPrimary,
    marginBottom: spacing.small,
  },
  inviteText: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  itemSection: {
    padding: spacing.medium,
  },
  itemCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    overflow: 'hidden',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  itemImage: {
    width: '100%',
    height: 200,
    resizeMode: 'cover',
  },
  itemInfo: {
    padding: spacing.medium,
  },
  itemName: {
    ...typography.h3,
    color: colors.textPrimary,
    marginBottom: spacing.small,
  },
  itemDescription: {
    ...typography.body,
    color: colors.textSecondary,
    marginBottom: spacing.medium,
  },
  priceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.small,
  },
  itemPrice: {
    ...typography.h4,
    color: colors.success,
    fontWeight: 'bold',
  },
  suggestedAmountContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    padding: spacing.small,
    borderRadius: 8,
    marginTop: spacing.small,
  },
  suggestedAmountLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginRight: spacing.small,
  },
  suggestedAmount: {
    ...typography.body,
    color: colors.primary,
    fontWeight: 'bold',
  },
  messageSection: {
    margin: spacing.medium,
    padding: spacing.medium,
    backgroundColor: 'white',
    borderRadius: 12,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  messageTitle: {
    ...typography.h4,
    color: colors.textPrimary,
    marginBottom: spacing.small,
  },
  messageText: {
    ...typography.body,
    color: colors.textSecondary,
    lineHeight: 24,
  },
  responseSection: {
    margin: spacing.medium,
    padding: spacing.medium,
    backgroundColor: 'white',
    borderRadius: 12,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  responseTitle: {
    ...typography.h4,
    color: colors.textPrimary,
    marginBottom: spacing.small,
  },
  responseInput: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    padding: spacing.medium,
    minHeight: 80,
    textAlignVertical: 'top',
    ...typography.body,
    color: colors.textPrimary,
  },
  buttonContainer: {
    flexDirection: 'row',
    padding: spacing.medium,
    gap: spacing.medium,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.medium,
    borderRadius: 12,
    gap: spacing.small,
  },
  acceptButton: {
    backgroundColor: colors.success,
  },
  declineButton: {
    backgroundColor: colors.error,
  },
  buttonText: {
    ...typography.button,
    color: 'white',
  },
  backButton: {
    marginTop: spacing.large,
    paddingVertical: spacing.medium,
    paddingHorizontal: spacing.large,
    backgroundColor: colors.primary,
    borderRadius: 8,
  },
  backButtonText: {
    ...typography.button,
    color: 'white',
  },
});

export default InvitationScreen; 