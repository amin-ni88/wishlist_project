import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import {
  TextInput,
  Button,
  Title,
  Card,
  Text,
  ActivityIndicator,
  Switch,
  Surface,
  Chip,
  List,
  Divider,
  Avatar,
  Portal,
  Modal,
} from 'react-native-paper';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import DateTimePicker from '@react-native-community/datetimepicker';
import { wishlistAPI } from '../services/api';
import { theme, colors } from '../utils/theme';
import { ResponsivePadding, isTablet } from '../components/common/ResponsiveLayout';

const { width } = Dimensions.get('window');

interface Occasion {
  id: string;
  title: string;
  icon: string;
  color: string;
}

const occasions: Occasion[] = [
  { id: 'birthday', title: 'تولد', icon: 'gift', color: colors.turquoise },
  { id: 'wedding', title: 'عروسی', icon: 'heart', color: colors.error },
  { id: 'graduation', title: 'فارغ‌التحصیلی', icon: 'school', color: colors.warning },
  { id: 'anniversary', title: 'سالگرد', icon: 'calendar-heart', color: colors.info },
  { id: 'newborn', title: 'تولد نوزاد', icon: 'baby', color: colors.success },
  { id: 'retirement', title: 'بازنشستگی', icon: 'briefcase', color: colors.tealDark },
  { id: 'holiday', title: 'تعطیلات', icon: 'beach', color: colors.mintLight },
  { id: 'other', title: 'سایر', icon: 'dots-horizontal', color: colors.grey600 },
];

export const CreateWishlistScreen = ({ navigation }: any) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    occasion_date: new Date(),
    is_public: true,
    occasion_type: '',
    category: '',
    theme_color: colors.turquoise,
  });
  const [loading, setLoading] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [occasionModalVisible, setOccasionModalVisible] = useState(false);
  const [selectedOccasion, setSelectedOccasion] = useState<Occasion | null>(null);

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const validateForm = () => {
    if (!formData.title.trim()) {
      Alert.alert('خطا', 'عنوان لیست آرزو الزامی است');
      return false;
    }
    if (formData.title.length < 3) {
      Alert.alert('خطا', 'عنوان باید حداقل ۳ کاراکتر باشد');
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setLoading(true);
    try {
      const wishlistData = {
        title: formData.title,
        description: formData.description,
        occasion_date: formData.occasion_date.toISOString().split('T')[0],
        is_public: formData.is_public,
        occasion_type: selectedOccasion?.id || 'other',
        theme_color: formData.theme_color,
      };

      const response = await wishlistAPI.createWishlist(wishlistData);
      
      Alert.alert(
        'موفقیت آمیز! 🎉',
        'لیست آرزوی شما با موفقیت ایجاد شد. حالا می‌توانید آیتم‌هایتان را اضافه کنید.',
        [
          { 
            text: 'مشاهده لیست', 
            onPress: () => {
              navigation.replace('ItemDetail', { 
                wishlistId: response.data.id 
              });
            }
          },
          { 
            text: 'بازگشت', 
            onPress: () => navigation.goBack() 
          }
        ]
      );
    } catch (error: any) {
      console.error('Error creating wishlist:', error);
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.title?.[0] ||
                          'خطا در ایجاد لیست آرزو';
      Alert.alert('خطا', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (event: any, selectedDate?: Date) => {
    setShowDatePicker(false);
    if (selectedDate) {
      handleInputChange('occasion_date', selectedDate);
    }
  };

  const selectOccasion = (occasion: Occasion) => {
    setSelectedOccasion(occasion);
    handleInputChange('occasion_type', occasion.id);
    handleInputChange('theme_color', occasion.color);
    setOccasionModalVisible(false);
  };

  const renderHeader = () => (
    <Surface style={styles.headerCard}>
      <LinearGradient
        colors={[formData.theme_color, colors.tealDark]}
        style={styles.headerGradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <View style={styles.headerContent}>
          <Avatar.Icon
            size={60}
            icon="gift-outline"
            style={[styles.headerIcon, { backgroundColor: 'rgba(255,255,255,0.2)' }]}
          />
          <Title style={styles.headerTitle}>لیست آرزوی جدید</Title>
          <Text style={styles.headerSubtitle}>
            رویاهایت رو به واقعیت تبدیل کن
          </Text>
        </View>
      </LinearGradient>
    </Surface>
  );

  const renderOccasionSelector = () => (
    <Card style={styles.sectionCard}>
      <Card.Content>
        <View style={styles.sectionHeader}>
          <Ionicons name="calendar" size={20} color={theme.colors.primary} />
          <Text style={styles.sectionTitle}>نوع مناسبت</Text>
        </View>
        
        <TouchableOpacity
          style={styles.occasionButton}
          onPress={() => setOccasionModalVisible(true)}
        >
          <View style={styles.occasionContent}>
            {selectedOccasion ? (
              <>
                <Ionicons
                  name={selectedOccasion.icon as any}
                  size={24}
                  color={selectedOccasion.color}
                />
                <Text style={styles.occasionText}>{selectedOccasion.title}</Text>
              </>
            ) : (
              <>
                <Ionicons name="add" size={24} color={theme.colors.disabled} />
                <Text style={[styles.occasionText, { color: theme.colors.disabled }]}>
                  انتخاب مناسبت
                </Text>
              </>
            )}
          </View>
          <Ionicons name="chevron-forward" size={20} color={theme.colors.disabled} />
        </TouchableOpacity>
      </Card.Content>
    </Card>
  );

  const renderDatePicker = () => (
    <Card style={styles.sectionCard}>
      <Card.Content>
        <View style={styles.sectionHeader}>
          <Ionicons name="time" size={20} color={theme.colors.primary} />
          <Text style={styles.sectionTitle}>تاریخ مناسبت</Text>
        </View>
        
        <TouchableOpacity
          style={styles.dateButton}
          onPress={() => setShowDatePicker(true)}
        >
          <View style={styles.dateContent}>
            <Ionicons name="calendar-outline" size={24} color={theme.colors.primary} />
            <Text style={styles.dateText}>
              {formData.occasion_date.toLocaleDateString('fa-IR')}
            </Text>
          </View>
                     <Ionicons name="chevron-forward" size={20} color={theme.colors.disabled} />
        </TouchableOpacity>
      </Card.Content>
    </Card>
  );

  const renderPrivacySettings = () => (
    <Card style={styles.sectionCard}>
      <Card.Content>
        <View style={styles.sectionHeader}>
          <Ionicons name="shield" size={20} color={theme.colors.primary} />
          <Text style={styles.sectionTitle}>تنظیمات حریم خصوصی</Text>
        </View>
        
        <View style={styles.privacyContainer}>
          <View style={styles.privacyOption}>
            <View style={styles.privacyLeft}>
              <Ionicons
                name={formData.is_public ? "globe" : "lock-closed"}
                size={24}
                color={formData.is_public ? colors.success : colors.warning}
              />
              <View style={styles.privacyText}>
                <Text style={styles.privacyTitle}>
                  {formData.is_public ? 'عمومی' : 'خصوصی'}
                </Text>
                <Text style={styles.privacyDescription}>
                  {formData.is_public 
                    ? 'همه می‌توانند ببینند و مشارکت کنند'
                    : 'فقط شما دسترسی دارید'
                  }
                </Text>
              </View>
            </View>
            <Switch
              value={formData.is_public}
              onValueChange={(value) => handleInputChange('is_public', value)}
              disabled={loading}
            />
          </View>
        </View>
      </Card.Content>
    </Card>
  );

  const renderOccasionModal = () => (
    <Portal>
      <Modal
        visible={occasionModalVisible}
        onDismiss={() => setOccasionModalVisible(false)}
        contentContainerStyle={styles.modal}
      >
        <Title style={styles.modalTitle}>انتخاب نوع مناسبت</Title>
        <ScrollView style={styles.modalScroll}>
          {occasions.map((occasion) => (
            <TouchableOpacity
              key={occasion.id}
              style={styles.occasionItem}
              onPress={() => selectOccasion(occasion)}
            >
              <View style={styles.occasionItemContent}>
                <Ionicons
                  name={occasion.icon as any}
                  size={24}
                  color={occasion.color}
                />
                <Text style={styles.occasionItemText}>{occasion.title}</Text>
              </View>
              {selectedOccasion?.id === occasion.id && (
                <Ionicons name="checkmark" size={20} color={colors.success} />
              )}
            </TouchableOpacity>
          ))}
        </ScrollView>
        <Button
          mode="outlined"
          onPress={() => setOccasionModalVisible(false)}
          style={styles.modalButton}
        >
          بستن
        </Button>
      </Modal>
    </Portal>
  );

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView 
        contentContainerStyle={styles.scrollContainer}
        showsVerticalScrollIndicator={false}
      >
        {renderHeader()}
        
        <Card style={styles.formCard}>
          <Card.Content>
            <TextInput
              label="عنوان لیست آرزو *"
              value={formData.title}
              onChangeText={(value) => handleInputChange('title', value)}
              mode="outlined"
              style={styles.input}
              disabled={loading}
              placeholder="مثل: جشن تولد ۲۵ سالگی من"
              left={<TextInput.Icon icon="format-title" />}
              maxLength={50}
            />

            <TextInput
              label="توضیحات"
              value={formData.description}
              onChangeText={(value) => handleInputChange('description', value)}
              mode="outlined"
              multiline
              numberOfLines={4}
              style={styles.input}
              disabled={loading}
              placeholder="چه چیزهایی رو آرزو داری و چرا این لیست رو ساختی..."
              left={<TextInput.Icon icon="text" />}
              maxLength={500}
            />
          </Card.Content>
        </Card>

        {renderOccasionSelector()}
        {renderDatePicker()}
        {renderPrivacySettings()}

        <View style={styles.buttonContainer}>
          <Button
            mode="contained"
            onPress={handleSubmit}
            style={[styles.submitButton, { backgroundColor: formData.theme_color }]}
            disabled={loading}
            icon="check"
          >
            {loading ? <ActivityIndicator color="white" /> : 'ایجاد لیست آرزو'}
          </Button>

          <Button
            mode="outlined"
            onPress={() => navigation.goBack()}
            style={styles.cancelButton}
            disabled={loading}
            icon="close"
          >
            لغو
          </Button>
        </View>
      </ScrollView>

      {showDatePicker && (
        <DateTimePicker
          value={formData.occasion_date}
          mode="date"
          display="default"
          onChange={handleDateChange}
          minimumDate={new Date()}
        />
      )}

      {renderOccasionModal()}
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  scrollContainer: {
    paddingBottom: 32,
  },
  headerCard: {
    margin: ResponsivePadding.horizontal,
    marginBottom: 16,
    borderRadius: 16,
    elevation: theme.elevation.medium,
    overflow: 'hidden',
  },
  headerGradient: {
    padding: 24,
  },
  headerContent: {
    alignItems: 'center',
  },
  headerIcon: {
    marginBottom: 12,
  },
  headerTitle: {
    color: 'white',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  headerSubtitle: {
    color: 'rgba(255,255,255,0.9)',
    fontSize: 16,
    textAlign: 'center',
  },
  formCard: {
    margin: ResponsivePadding.horizontal,
    marginBottom: 16,
    elevation: theme.elevation.small,
  },
  sectionCard: {
    margin: ResponsivePadding.horizontal,
    marginBottom: 16,
    elevation: theme.elevation.small,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
    color: theme.colors.text,
  },
  input: {
    marginBottom: 16,
  },
  occasionButton: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.grey300,
  },
  occasionContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  occasionText: {
    marginLeft: 12,
    fontSize: 16,
    color: theme.colors.text,
  },
  dateButton: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.grey300,
  },
  dateContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dateText: {
    marginLeft: 12,
    fontSize: 16,
    color: theme.colors.text,
  },
  privacyContainer: {
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.grey300,
  },
  privacyOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
  },
  privacyLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  privacyText: {
    marginLeft: 12,
    flex: 1,
  },
  privacyTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  privacyDescription: {
    fontSize: 14,
    color: theme.colors.disabled,
    marginTop: 2,
  },
  buttonContainer: {
    margin: ResponsivePadding.horizontal,
    gap: 12,
  },
  submitButton: {
    paddingVertical: 8,
  },
  cancelButton: {
    paddingVertical: 8,
  },
  modal: {
    backgroundColor: theme.colors.surface,
    padding: 20,
    margin: 20,
    borderRadius: 12,
    maxHeight: '80%',
  },
  modalTitle: {
    textAlign: 'center',
    marginBottom: 20,
  },
  modalScroll: {
    maxHeight: 400,
  },
  occasionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.grey200,
  },
  occasionItemContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  occasionItemText: {
    marginLeft: 12,
    fontSize: 16,
    color: theme.colors.text,
  },
  modalButton: {
    marginTop: 16,
  },
}); 