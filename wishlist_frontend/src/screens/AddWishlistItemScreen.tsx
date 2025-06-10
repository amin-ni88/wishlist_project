import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
  KeyboardAvoidingView,
  Platform,
  TouchableOpacity,
  Image,
  Dimensions,
} from 'react-native';
import {
  TextInput,
  Button,
  Title,
  Card,
  Text,
  ActivityIndicator,
  Chip,
  Menu,
  Surface,
  Avatar,
  IconButton,
  Portal,
  Modal,
  Divider,
  List,
} from 'react-native-paper';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import * as ImagePicker from 'expo-image-picker';
import { wishlistAPI, itemAPI } from '../services/api';
import { theme, colors } from '../utils/theme';
import { ResponsivePadding, isTablet } from '../components/common/ResponsiveLayout';
import LoadingScreen from '../components/common/LoadingScreen';

const { width } = Dimensions.get('window');

interface Wishlist {
  id: number;
  title: string;
  occasion_type?: string;
  items_count?: number;
}

interface PriceSuggestion {
  category: string;
  price_range: {
    min: number;
    max: number;
    average: number;
  };
}

const priorityLevels = [
  { value: 1, label: 'کم', color: colors.success, icon: 'flag-outline' },
  { value: 2, label: 'متوسط', color: colors.warning, icon: 'flag' },
  { value: 3, label: 'بالا', color: colors.error, icon: 'flag' },
  { value: 4, label: 'خیلی بالا', color: colors.darkBlue, icon: 'flag' },
  { value: 5, label: 'ضروری', color: colors.navy, icon: 'flag' },
];

const popularTags = [
  'الکترونیک', 'کتاب', 'لباس', 'ورزشی', 'خانه و آشپزخانه',
  'زیبایی', 'سفر', 'موسیقی', 'هنر', 'بازی', 'فیلم', 'طلا و جواهر'
];

export const AddWishlistItemScreen = ({ navigation, route }: any) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    product_url: '',
    wishlist_id: route?.params?.wishlistId || '',
    priority: 1,
    tags: [] as string[],
  });
  const [wishlists, setWishlists] = useState<Wishlist[]>([]);
  const [selectedImages, setSelectedImages] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingWishlists, setLoadingWishlists] = useState(true);
  const [menuVisible, setMenuVisible] = useState(false);
  const [selectedWishlist, setSelectedWishlist] = useState<Wishlist | null>(null);
  const [tagModalVisible, setTagModalVisible] = useState(false);
  const [customTag, setCustomTag] = useState('');
  const [priceSuggestions, setPriceSuggestions] = useState<PriceSuggestion[]>([]);

  useEffect(() => {
    loadWishlists();
    requestImagePermission();
  }, []);

  const requestImagePermission = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('اجازه دسترسی', 'برای انتخاب تصاویر نیاز به اجازه دسترسی داریم');
    }
  };

  const loadWishlists = async () => {
    try {
      const response = await wishlistAPI.getWishlists();
      const wishlistData = response.data.results || response.data;
      setWishlists(wishlistData);
      
      if (formData.wishlist_id) {
        const selected = wishlistData.find((w: Wishlist) => w.id === parseInt(formData.wishlist_id));
        if (selected) {
          setSelectedWishlist(selected);
        }
      }
    } catch (error) {
      console.error('Error loading wishlists:', error);
      Alert.alert('خطا', 'خطا در بارگذاری لیست آرزوها');
    } finally {
      setLoadingWishlists(false);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const pickImages = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsMultipleSelection: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets) {
        const newImages = result.assets.map(asset => asset.uri);
        setSelectedImages(prev => [...prev, ...newImages].slice(0, 5)); // Max 5 images
      }
    } catch (error) {
      Alert.alert('خطا', 'خطا در انتخاب تصاویر');
    }
  };

  const removeImage = (index: number) => {
    setSelectedImages(prev => prev.filter((_, i) => i !== index));
  };

  const addTag = (tag: string) => {
    if (tag.trim() && !formData.tags.includes(tag.trim())) {
      handleInputChange('tags', [...formData.tags, tag.trim()]);
    }
  };

  const removeTag = (tagToRemove: string) => {
    handleInputChange('tags', formData.tags.filter(tag => tag !== tagToRemove));
  };

  const validateForm = () => {
    if (!formData.name.trim()) {
      Alert.alert('خطا', 'نام آیتم الزامی است');
      return false;
    }
    if (formData.name.length < 3) {
      Alert.alert('خطا', 'نام آیتم باید حداقل ۳ کاراکتر باشد');
      return false;
    }
    if (!formData.price.trim()) {
      Alert.alert('خطا', 'قیمت الزامی است');
      return false;
    }
    const price = parseFloat(formData.price);
    if (isNaN(price) || price <= 0) {
      Alert.alert('خطا', 'قیمت باید عدد مثبت باشد');
      return false;
    }
    if (!selectedWishlist) {
      Alert.alert('خطا', 'لطفا یک لیست آرزو انتخاب کنید');
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setLoading(true);
    try {
      const itemData = {
        ...formData,
        price: parseFloat(formData.price),
        wishlist: selectedWishlist!.id,
        images: selectedImages,
      };

      const response = await itemAPI.createItem(itemData);
      
      Alert.alert(
        'عالی! 🎉',
        'آیتم با موفقیت به لیست آرزوهایتان اضافه شد.',
        [
          { 
            text: 'مشاهده آیتم', 
            onPress: () => {
              navigation.replace('ItemDetail', { 
                itemId: response.data.id,
                wishlistId: selectedWishlist!.id 
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
      console.error('Error creating item:', error);
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.name?.[0] ||
                          'خطا در ایجاد آیتم';
      Alert.alert('خطا', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const selectWishlist = (wishlist: Wishlist) => {
    setSelectedWishlist(wishlist);
    setFormData(prev => ({ ...prev, wishlist_id: wishlist.id.toString() }));
    setMenuVisible(false);
  };

  const renderHeader = () => (
    <Surface style={styles.headerCard}>
      <LinearGradient
        colors={[colors.turquoise, colors.tealDark]}
        style={styles.headerGradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <View style={styles.headerContent}>
          <Avatar.Icon
            size={60}
            icon="plus"
            style={[styles.headerIcon, { backgroundColor: 'rgba(255,255,255,0.2)' }]}
          />
          <Title style={styles.headerTitle}>افزودن آیتم جدید</Title>
          <Text style={styles.headerSubtitle}>
            آرزوی جدیدت رو اضافه کن
          </Text>
        </View>
      </LinearGradient>
    </Surface>
  );

  const renderWishlistSelector = () => (
    <Card style={styles.sectionCard}>
      <Card.Content>
        <View style={styles.sectionHeader}>
          <Ionicons name="list" size={20} color={theme.colors.primary} />
          <Text style={styles.sectionTitle}>انتخاب لیست آرزو</Text>
        </View>
        
        <Menu
          visible={menuVisible}
          onDismiss={() => setMenuVisible(false)}
          anchor={
            <TouchableOpacity
              style={styles.wishlistButton}
              onPress={() => setMenuVisible(true)}
            >
              <View style={styles.wishlistContent}>
                {selectedWishlist ? (
                  <>
                    <Ionicons name="gift" size={24} color={colors.turquoise} />
                    <View style={styles.wishlistInfo}>
                      <Text style={styles.wishlistTitle}>{selectedWishlist.title}</Text>
                      <Text style={styles.wishlistSubtitle}>
                        {selectedWishlist.items_count || 0} آیتم
                      </Text>
                    </View>
                  </>
                ) : (
                  <>
                    <Ionicons name="add" size={24} color={theme.colors.disabled} />
                    <Text style={[styles.wishlistTitle, { color: theme.colors.disabled }]}>
                      انتخاب لیست آرزو
                    </Text>
                  </>
                )}
              </View>
              <Ionicons name="chevron-forward" size={20} color={theme.colors.disabled} />
            </TouchableOpacity>
          }
        >
          {wishlists.map((wishlist) => (
            <Menu.Item
              key={wishlist.id}
              onPress={() => selectWishlist(wishlist)}
              title={wishlist.title}
              leadingIcon="gift"
            />
          ))}
        </Menu>
      </Card.Content>
    </Card>
  );

  const renderImagePicker = () => (
    <Card style={styles.sectionCard}>
      <Card.Content>
        <View style={styles.sectionHeader}>
          <Ionicons name="camera" size={20} color={theme.colors.primary} />
          <Text style={styles.sectionTitle}>تصاویر محصول</Text>
          <Text style={styles.optional}>(اختیاری)</Text>
        </View>
        
        <ScrollView horizontal style={styles.imageContainer} showsHorizontalScrollIndicator={false}>
          {selectedImages.map((image, index) => (
            <View key={index} style={styles.imageWrapper}>
              <Image source={{ uri: image }} style={styles.selectedImage} />
              <TouchableOpacity
                style={styles.removeImageButton}
                onPress={() => removeImage(index)}
              >
                <Ionicons name="close" size={16} color="white" />
              </TouchableOpacity>
            </View>
          ))}
          
          {selectedImages.length < 5 && (
            <TouchableOpacity style={styles.addImageButton} onPress={pickImages}>
              <Ionicons name="camera-outline" size={32} color={theme.colors.disabled} />
              <Text style={styles.addImageText}>افزودن تصویر</Text>
            </TouchableOpacity>
          )}
        </ScrollView>
        
        <Text style={styles.imageNote}>
          حداکثر ۵ تصویر می‌توانید اضافه کنید
        </Text>
      </Card.Content>
    </Card>
  );

  const renderBasicInfo = () => (
    <Card style={styles.sectionCard}>
      <Card.Content>
        <View style={styles.sectionHeader}>
          <Ionicons name="information-circle" size={20} color={theme.colors.primary} />
          <Text style={styles.sectionTitle}>اطلاعات پایه</Text>
        </View>
        
        <TextInput
          label="نام آیتم *"
          value={formData.name}
          onChangeText={(value) => handleInputChange('name', value)}
          mode="outlined"
          style={styles.input}
          disabled={loading}
          left={<TextInput.Icon icon="tag" />}
          placeholder="مثل: گوشی iPhone 15 Pro"
          maxLength={100}
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
          left={<TextInput.Icon icon="text" />}
          placeholder="چرا این رو می‌خوای و چه ویژگی‌هایی داره..."
          maxLength={500}
        />

        <TextInput
          label="قیمت (تومان) *"
          value={formData.price}
          onChangeText={(value) => handleInputChange('price', value)}
          mode="outlined"
          keyboardType="numeric"
          style={styles.input}
          disabled={loading}
          left={<TextInput.Icon icon="cash" />}
          placeholder="۱۰۰۰۰۰۰"
        />

        <TextInput
          label="لینک محصول"
          value={formData.product_url}
          onChangeText={(value) => handleInputChange('product_url', value)}
          mode="outlined"
          style={styles.input}
          keyboardType="url"
          autoCapitalize="none"
          disabled={loading}
          left={<TextInput.Icon icon="link" />}
          placeholder="https://example.com/product"
        />
      </Card.Content>
    </Card>
  );

  const renderPriority = () => (
    <Card style={styles.sectionCard}>
      <Card.Content>
        <View style={styles.sectionHeader}>
          <Ionicons name="flag" size={20} color={theme.colors.primary} />
          <Text style={styles.sectionTitle}>سطح اولویت</Text>
        </View>
        
        <View style={styles.priorityContainer}>
          {priorityLevels.map((level) => (
            <TouchableOpacity
              key={level.value}
              style={[
                styles.priorityItem,
                formData.priority === level.value && styles.selectedPriority,
                { borderColor: level.color }
              ]}
              onPress={() => handleInputChange('priority', level.value)}
            >
              <Ionicons
                name={level.icon as any}
                size={20}
                color={formData.priority === level.value ? 'white' : level.color}
              />
              <Text style={[
                styles.priorityText,
                formData.priority === level.value && styles.selectedPriorityText
              ]}>
                {level.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </Card.Content>
    </Card>
  );

  const renderTags = () => (
    <Card style={styles.sectionCard}>
      <Card.Content>
        <View style={styles.sectionHeader}>
          <Ionicons name="pricetag" size={20} color={theme.colors.primary} />
          <Text style={styles.sectionTitle}>برچسب‌ها</Text>
          <Text style={styles.optional}>(اختیاری)</Text>
        </View>
        
        {formData.tags.length > 0 && (
          <View style={styles.selectedTags}>
            {formData.tags.map((tag, index) => (
              <Chip
                key={index}
                style={styles.selectedTag}
                onClose={() => removeTag(tag)}
                textStyle={styles.tagText}
              >
                {tag}
              </Chip>
            ))}
          </View>
        )}
        
        <TouchableOpacity
          style={styles.addTagButton}
          onPress={() => setTagModalVisible(true)}
        >
          <Ionicons name="add" size={20} color={colors.turquoise} />
          <Text style={styles.addTagText}>افزودن برچسب</Text>
        </TouchableOpacity>
      </Card.Content>
    </Card>
  );

  const renderTagModal = () => (
    <Portal>
      <Modal
        visible={tagModalVisible}
        onDismiss={() => setTagModalVisible(false)}
        contentContainerStyle={styles.modal}
      >
        <Title style={styles.modalTitle}>انتخاب برچسب</Title>
        
        <TextInput
          label="برچسب سفارشی"
          value={customTag}
          onChangeText={setCustomTag}
          mode="outlined"
          style={styles.modalInput}
          right={
            <TextInput.Icon
              icon="plus"
              onPress={() => {
                if (customTag.trim()) {
                  addTag(customTag);
                  setCustomTag('');
                }
              }}
            />
          }
        />
        
        <Text style={styles.popularTagsTitle}>برچسب‌های محبوب:</Text>
        <View style={styles.popularTags}>
          {popularTags.map((tag, index) => (
            <Chip
              key={index}
              style={styles.popularTag}
              onPress={() => addTag(tag)}
              disabled={formData.tags.includes(tag)}
            >
              {tag}
            </Chip>
          ))}
        </View>
        
        <Button
          mode="outlined"
          onPress={() => setTagModalVisible(false)}
          style={styles.modalButton}
        >
          بستن
        </Button>
      </Modal>
    </Portal>
  );

  if (loadingWishlists) {
    return <LoadingScreen message="در حال بارگذاری لیست آرزوها..." />;
  }

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
        {renderWishlistSelector()}
        {renderImagePicker()}
        {renderBasicInfo()}
        {renderPriority()}
        {renderTags()}

        <View style={styles.buttonContainer}>
          <Button
            mode="contained"
            onPress={handleSubmit}
            style={[styles.submitButton, { backgroundColor: colors.turquoise }]}
            disabled={loading || !selectedWishlist}
            icon="check"
            contentStyle={styles.buttonContent}
          >
            {loading ? <ActivityIndicator color="white" /> : 'افزودن آیتم'}
          </Button>

          <Button
            mode="outlined"
            onPress={() => navigation.goBack()}
            style={styles.cancelButton}
            disabled={loading}
            icon="close"
            contentStyle={styles.buttonContent}
          >
            لغو
          </Button>
        </View>
      </ScrollView>

      {renderTagModal()}
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
    elevation: theme.elevation.medium,
    overflow: 'hidden',
  },
  headerGradient: {
    padding: ResponsivePadding.horizontal,
    paddingVertical: 24,
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
    flex: 1,
  },
  optional: {
    fontSize: 12,
    color: theme.colors.disabled,
    fontStyle: 'italic',
  },
  wishlistButton: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.grey300,
  },
  wishlistContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  wishlistInfo: {
    marginLeft: 12,
  },
  wishlistTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  wishlistSubtitle: {
    fontSize: 12,
    color: theme.colors.disabled,
  },
  imageContainer: {
    marginBottom: 12,
  },
  imageWrapper: {
    position: 'relative',
    marginRight: 12,
  },
  selectedImage: {
    width: 80,
    height: 80,
    borderRadius: 8,
  },
  removeImageButton: {
    position: 'absolute',
    top: -8,
    right: -8,
    backgroundColor: colors.error,
    borderRadius: 12,
    width: 24,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  addImageButton: {
    width: 80,
    height: 80,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: theme.colors.grey300,
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
  },
  addImageText: {
    fontSize: 10,
    color: theme.colors.disabled,
    marginTop: 4,
    textAlign: 'center',
  },
  imageNote: {
    fontSize: 12,
    color: theme.colors.disabled,
    textAlign: 'center',
  },
  input: {
    marginBottom: 16,
  },
  priorityContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  priorityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 8,
    borderWidth: 2,
    backgroundColor: 'transparent',
    minWidth: '30%',
  },
  selectedPriority: {
    backgroundColor: colors.turquoise,
  },
  priorityText: {
    marginLeft: 8,
    fontSize: 14,
    fontWeight: 'bold',
  },
  selectedPriorityText: {
    color: 'white',
  },
  selectedTags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 12,
  },
  selectedTag: {
    backgroundColor: colors.turquoise,
  },
  tagText: {
    color: 'white',
    fontSize: 12,
  },
  addTagButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.turquoise,
    borderStyle: 'dashed',
  },
  addTagText: {
    marginLeft: 8,
    color: colors.turquoise,
    fontWeight: 'bold',
  },
  buttonContainer: {
    margin: ResponsivePadding.horizontal,
    gap: 12,
  },
  submitButton: {
    borderRadius: 8,
  },
  cancelButton: {
    borderRadius: 8,
    borderColor: colors.turquoise,
  },
  buttonContent: {
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
  modalInput: {
    marginBottom: 16,
  },
  popularTagsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
    color: theme.colors.text,
  },
  popularTags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 20,
  },
  popularTag: {
    backgroundColor: theme.colors.grey200,
  },
  modalButton: {
    marginTop: 16,
  },
});
