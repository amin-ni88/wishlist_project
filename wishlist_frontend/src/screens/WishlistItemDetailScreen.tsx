import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
  RefreshControl,
  Image,
  Dimensions,
  TouchableOpacity,
  Linking,
  Share,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Text,
  ActivityIndicator,
  ProgressBar,
  Chip,
  Divider,
  TextInput,
  Dialog,
  Portal,
  Surface,
  Avatar,
  IconButton,
  List,
  FAB,
} from 'react-native-paper';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { itemAPI } from '../services/api';
import { theme, colors } from '../utils/theme';
import { ResponsivePadding, isTablet } from '../components/common/ResponsiveLayout';
import LoadingScreen from '../components/common/LoadingScreen';

const { width, height } = Dimensions.get('window');

interface WishlistItem {
  id: number;
  name: string;
  description: string;
  price: number;
  product_url: string;
  images?: string[];
  status: string;
  priority: number;
  wishlist: {
    id: number;
    title: string;
    owner: {
      id: number;
      username: string;
      first_name: string;
      last_name: string;
      profile_image?: string;
    };
  };
  total_contributions: number;
  remaining_amount: number;
  contribution_percentage: number;
  contributors_count: number;
  created_at: string;
  updated_at: string;
  tags?: string[];
}

interface Contributor {
  id: number;
  user: {
    first_name: string;
    last_name: string;
    username: string;
    profile_image?: string;
  };
  amount: number;
  message?: string;
  created_at: string;
  is_anonymous: boolean;
}

export const WishlistItemDetailScreen = ({ navigation, route }: any) => {
  const [item, setItem] = useState<WishlistItem | null>(null);
  const [contributors, setContributors] = useState<Contributor[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [imageModalVisible, setImageModalVisible] = useState(false);
  const [contributionDialogVisible, setContributionDialogVisible] = useState(false);
  const [contributionAmount, setContributionAmount] = useState('');
  const [contributionMessage, setContributionMessage] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [contributionLoading, setContributionLoading] = useState(false);

  const { itemId, wishlistId } = route.params;

  useEffect(() => {
    loadItemDetails();
    loadContributors();
  }, []);

  const loadItemDetails = async () => {
    try {
      const response = await itemAPI.getItem(itemId);
      setItem(response.data);
    } catch (error) {
      console.error('Error loading item details:', error);
      Alert.alert('خطا', 'خطا در بارگذاری جزئیات آیتم');
      navigation.goBack();
    } finally {
      setLoading(false);
    }
  };

  const loadContributors = async () => {
    try {
      const response = await itemAPI.getItemContributors(itemId);
      setContributors(response.data.results || []);
    } catch (error) {
      console.error('Error loading contributors:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([loadItemDetails(), loadContributors()]);
    setRefreshing(false);
  };

  const handleContribute = async () => {
    if (!contributionAmount.trim()) {
      Alert.alert('خطا', 'لطفا مبلغ کمک را وارد کنید');
      return;
    }

    const amount = parseFloat(contributionAmount);
    if (isNaN(amount) || amount <= 0) {
      Alert.alert('خطا', 'مبلغ کمک باید عدد مثبت باشد');
      return;
    }

    if (item && amount > item.remaining_amount) {
      Alert.alert('خطا', 'مبلغ کمک نمی‌تواند بیشتر از مبلغ باقی‌مانده باشد');
      return;
    }

    setContributionLoading(true);
    try {
      await itemAPI.contribute(itemId, {
        amount,
        message: contributionMessage,
        is_anonymous: isAnonymous,
      });

      Alert.alert(
        'عالی! 🎉',
        'کمک شما با موفقیت ثبت شد. از همدلی شما متشکریم!',
        [{ text: 'باشه', onPress: () => {
          setContributionDialogVisible(false);
          setContributionAmount('');
          setContributionMessage('');
          setIsAnonymous(false);
          onRefresh();
        }}]
      );
    } catch (error: any) {
      console.error('Error contributing:', error);
      const errorMessage = error.response?.data?.error || 
                          'خطا در ثبت کمک';
      Alert.alert('خطا', errorMessage);
    } finally {
      setContributionLoading(false);
    }
  };

  const openProductUrl = async () => {
    if (item?.product_url) {
      try {
        await Linking.openURL(item.product_url);
      } catch (error) {
        Alert.alert('خطا', 'امکان باز کردن لینک وجود ندارد');
      }
    }
  };

  const shareItem = async () => {
    navigation.navigate('ShareWishlist' as never, { wishlistItem: item } as never);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'AVAILABLE':
        return colors.success;
      case 'IN_PROGRESS':
        return colors.warning;
      case 'FULFILLED':
        return colors.info;
      default:
        return colors.grey500;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'AVAILABLE':
        return 'در دسترس';
      case 'IN_PROGRESS':
        return 'در حال تامین';
      case 'FULFILLED':
        return 'تامین شده';
      default:
        return status;
    }
  };

  const getPriorityText = (priority: number) => {
    const priorities = ['', 'کم', 'متوسط', 'بالا', 'خیلی بالا', 'ضروری'];
    return priorities[priority] || priority.toString();
  };

  const getPriorityColor = (priority: number) => {
    const priorityColors = [
      colors.grey500, 
      colors.success, 
      colors.warning, 
      colors.error, 
      colors.darkBlue, 
      colors.darkBlue
    ];
    return priorityColors[priority] || colors.grey500;
  };

  const renderImageGallery = () => {
    if (!item?.images || item.images.length === 0) {
      return (
        <Surface style={styles.placeholderImage}>
          <Ionicons name="image-outline" size={64} color={theme.colors.disabled} />
          <Text style={styles.placeholderText}>بدون تصویر</Text>
        </Surface>
      );
    }

    return (
      <View style={styles.imageGallery}>
        <TouchableOpacity 
          onPress={() => setImageModalVisible(true)}
          style={styles.mainImageContainer}
        >
          <Image 
            source={{ uri: item.images[selectedImageIndex] }} 
            style={styles.mainImage}
            resizeMode="cover"
          />
          <View style={styles.imageOverlay}>
            <Ionicons name="expand" size={24} color="white" />
          </View>
        </TouchableOpacity>
        
        {item.images.length > 1 && (
          <ScrollView 
            horizontal 
            style={styles.thumbnailContainer}
            showsHorizontalScrollIndicator={false}
          >
            {item.images.map((image, index) => (
              <TouchableOpacity
                key={index}
                onPress={() => setSelectedImageIndex(index)}
                style={[
                  styles.thumbnail,
                  selectedImageIndex === index && styles.selectedThumbnail
                ]}
              >
                <Image source={{ uri: image }} style={styles.thumbnailImage} />
              </TouchableOpacity>
            ))}
          </ScrollView>
        )}
      </View>
    );
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
          <View style={styles.headerTop}>
            <View style={styles.ownerInfo}>
              <Avatar.Image
                size={40}
                source={{ uri: item?.wishlist.owner.profile_image || undefined }}
                style={styles.ownerAvatar}
              />
              <View style={styles.ownerDetails}>
                <Text style={styles.ownerName}>
                  {item?.wishlist.owner.first_name || item?.wishlist.owner.username}
                </Text>
                <Text style={styles.wishlistTitle}>{item?.wishlist.title}</Text>
              </View>
            </View>
            <View style={styles.headerActions}>
              <IconButton
                icon="share"
                iconColor="white"
                size={24}
                onPress={shareItem}
                style={styles.headerButton}
              />
            </View>
          </View>
        </View>
      </LinearGradient>
    </Surface>
  );

  const renderItemInfo = () => (
    <Card style={styles.infoCard}>
      <Card.Content>
        <View style={styles.titleRow}>
          <Title style={styles.itemTitle}>{item?.name}</Title>
          <View style={styles.statusChips}>
            <Chip
              style={[styles.statusChip, { backgroundColor: getStatusColor(item?.status || '') }]}
              textStyle={styles.chipText}
            >
              {getStatusText(item?.status || '')}
            </Chip>
            <Chip
              style={[styles.priorityChip, { backgroundColor: getPriorityColor(item?.priority || 0) }]}
              textStyle={styles.chipText}
            >
              {getPriorityText(item?.priority || 0)}
            </Chip>
          </View>
        </View>

        {item?.description && (
          <Paragraph style={styles.description}>{item.description}</Paragraph>
        )}

        {item?.tags && item.tags.length > 0 && (
          <View style={styles.tagsContainer}>
            {item.tags.map((tag, index) => (
              <Chip
                key={index}
                style={styles.tag}
                textStyle={styles.tagText}
                compact
              >
                {tag}
              </Chip>
            ))}
          </View>
        )}
      </Card.Content>
    </Card>
  );

  const renderPriceProgress = () => (
    <Card style={styles.progressCard}>
      <Card.Content>
        <View style={styles.priceHeader}>
          <Text style={styles.priceLabel}>هدف مالی</Text>
          <Text style={styles.price}>{item?.price.toLocaleString()} تومان</Text>
        </View>

        <View style={styles.progressInfo}>
          <View style={styles.progressItem}>
            <Text style={styles.progressValue}>
              {item?.total_contributions?.toLocaleString() || 0}
            </Text>
            <Text style={styles.progressLabel}>تامین شده</Text>
          </View>
          <View style={styles.progressItem}>
            <Text style={[styles.progressValue, { color: colors.error }]}>
              {item?.remaining_amount?.toLocaleString() || 0}
            </Text>
            <Text style={styles.progressLabel}>باقی‌مانده</Text>
          </View>
          <View style={styles.progressItem}>
            <Text style={[styles.progressValue, { color: colors.turquoise }]}>
              {item?.contributors_count || 0}
            </Text>
            <Text style={styles.progressLabel}>مشارکت‌کننده</Text>
          </View>
        </View>

        <ProgressBar
          progress={(item?.contribution_percentage || 0) / 100}
          color={colors.turquoise}
          style={styles.progressBar}
        />
        <Text style={styles.progressText}>
          {item?.contribution_percentage?.toFixed(1) || 0}% تکمیل شده
        </Text>
      </Card.Content>
    </Card>
  );

  const renderContributors = () => (
    <Card style={styles.contributorsCard}>
      <Card.Content>
        <View style={styles.contributorsHeader}>
          <Ionicons name="people" size={20} color={theme.colors.primary} />
          <Text style={styles.contributorsTitle}>مشارکت‌کنندگان</Text>
        </View>
        
        {contributors.length === 0 ? (
          <View style={styles.noContributors}>
            <Ionicons name="heart-outline" size={48} color={theme.colors.disabled} />
            <Text style={styles.noContributorsText}>
              هنوز کسی کمک نکرده. اولین نفر باش! 💚
            </Text>
          </View>
        ) : (
          <View style={styles.contributorsList}>
            {contributors.slice(0, 5).map((contributor, index) => (
              <View key={index} style={styles.contributorItem}>
                <Avatar.Text
                  size={40}
                  label={contributor.is_anonymous ? '؟' : 
                    (contributor.user.first_name?.charAt(0) || contributor.user.username.charAt(0))}
                  style={styles.contributorAvatar}
                />
                <View style={styles.contributorInfo}>
                  <Text style={styles.contributorName}>
                    {contributor.is_anonymous ? 'ناشناس' : 
                      (contributor.user.first_name || contributor.user.username)}
                  </Text>
                  <Text style={styles.contributorAmount}>
                    {contributor.amount.toLocaleString()} تومان
                  </Text>
                  {contributor.message && (
                    <Text style={styles.contributorMessage}>{contributor.message}</Text>
                  )}
                </View>
                <Text style={styles.contributorDate}>
                  {new Date(contributor.created_at).toLocaleDateString('fa-IR')}
                </Text>
              </View>
            ))}
            {contributors.length > 5 && (
              <TouchableOpacity style={styles.moreContributors}>
                <Text style={styles.moreContributorsText}>
                  مشاهده {contributors.length - 5} نفر دیگر
                </Text>
              </TouchableOpacity>
            )}
          </View>
        )}
      </Card.Content>
    </Card>
  );

  const renderActions = () => (
    <Card style={styles.actionsCard}>
      <Card.Content>
        <View style={styles.actionsContainer}>
          {item?.status !== 'FULFILLED' && (
            <Button
              mode="contained"
              onPress={() => setContributionDialogVisible(true)}
              style={[styles.contributeButton, { backgroundColor: colors.turquoise }]}
              icon="heart"
              contentStyle={styles.buttonContent}
            >
              کمک کردن
            </Button>
          )}

          <Button
            mode="outlined"
            onPress={shareItem}
            style={styles.shareButton}
            icon="share"
            contentStyle={styles.buttonContent}
          >
            اشتراک‌گذاری
          </Button>

          {item?.product_url && (
            <Button
              mode="outlined"
              onPress={openProductUrl}
              style={styles.linkButton}
              icon="open-in-new"
              contentStyle={styles.buttonContent}
            >
              مشاهده محصول
            </Button>
          )}
        </View>

        <Text style={styles.dateText}>
          ایجاد شده: {item && new Date(item.created_at).toLocaleDateString('fa-IR')}
        </Text>
      </Card.Content>
    </Card>
  );

  const renderContributionDialog = () => (
    <Portal>
      <Dialog
        visible={contributionDialogVisible}
        onDismiss={() => setContributionDialogVisible(false)}
        style={styles.dialog}
      >
        <Dialog.Title style={styles.dialogTitle}>
          <Ionicons name="heart" size={24} color={colors.turquoise} />
          کمک به آرزو
        </Dialog.Title>
        <Dialog.Content>
          <TextInput
            label="مبلغ کمک (تومان)"
            value={contributionAmount}
            onChangeText={setContributionAmount}
            keyboardType="numeric"
            mode="outlined"
            style={styles.dialogInput}
            left={<TextInput.Icon icon="cash" />}
          />
          <TextInput
            label="پیام دلگرمی (اختیاری)"
            value={contributionMessage}
            onChangeText={setContributionMessage}
            multiline
            numberOfLines={3}
            mode="outlined"
            style={styles.dialogInput}
            left={<TextInput.Icon icon="message" />}
          />
          
          <View style={styles.anonymousContainer}>
            <Text style={styles.anonymousLabel}>کمک ناشناس</Text>
            <IconButton
              icon={isAnonymous ? "checkbox-marked" : "checkbox-blank-outline"}
              iconColor={isAnonymous ? colors.turquoise : theme.colors.disabled}
              onPress={() => setIsAnonymous(!isAnonymous)}
            />
          </View>
          
          <Surface style={styles.remainingInfo}>
            <Text style={styles.remainingInfoText}>
              💰 مبلغ باقی‌مانده: {item?.remaining_amount?.toLocaleString() || 0} تومان
            </Text>
          </Surface>
        </Dialog.Content>
        <Dialog.Actions>
          <Button onPress={() => setContributionDialogVisible(false)}>
            لغو
          </Button>
          <Button
            mode="contained"
            onPress={handleContribute}
            loading={contributionLoading}
            style={{ backgroundColor: colors.turquoise }}
          >
            کمک کردن 💚
          </Button>
        </Dialog.Actions>
      </Dialog>
    </Portal>
  );

  if (loading) {
    return <LoadingScreen message="در حال بارگذاری جزئیات..." />;
  }

  if (!item) {
    return (
      <View style={styles.errorContainer}>
        <Ionicons name="sad-outline" size={64} color={theme.colors.disabled} />
        <Text style={styles.errorText}>آیتم یافت نشد</Text>
        <Button 
          mode="contained" 
          onPress={() => navigation.goBack()}
          style={{ backgroundColor: colors.turquoise }}
        >
          بازگشت
        </Button>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        showsVerticalScrollIndicator={false}
      >
        {renderHeader()}
        {renderImageGallery()}
        {renderItemInfo()}
        {renderPriceProgress()}
        {renderContributors()}
        {renderActions()}
      </ScrollView>

      {item.status !== 'FULFILLED' && (
        <FAB
          style={[styles.fab, { backgroundColor: colors.turquoise }]}
          icon="heart"
          onPress={() => setContributionDialogVisible(true)}
          label={isTablet ? 'کمک کن' : undefined}
        />
      )}

      {renderContributionDialog()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: ResponsivePadding.horizontal,
  },
  errorText: {
    fontSize: 18,
    marginVertical: 16,
    textAlign: 'center',
    color: theme.colors.text,
  },
  headerCard: {
    elevation: theme.elevation.medium,
    overflow: 'hidden',
  },
  headerGradient: {
    padding: ResponsivePadding.horizontal,
    paddingVertical: 20,
  },
  headerContent: {
    flex: 1,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  ownerInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  ownerAvatar: {
    backgroundColor: 'rgba(255,255,255,0.2)',
  },
  ownerDetails: {
    marginLeft: 12,
    flex: 1,
  },
  ownerName: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  wishlistTitle: {
    color: 'rgba(255,255,255,0.9)',
    fontSize: 14,
  },
  headerActions: {
    flexDirection: 'row',
  },
  headerButton: {
    backgroundColor: 'rgba(255,255,255,0.2)',
  },
  imageGallery: {
    margin: ResponsivePadding.horizontal,
    marginTop: 16,
  },
  placeholderImage: {
    height: 200,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.grey100,
  },
  placeholderText: {
    marginTop: 8,
    color: theme.colors.disabled,
  },
  mainImageContainer: {
    position: 'relative',
    borderRadius: 12,
    overflow: 'hidden',
    elevation: theme.elevation.small,
  },
  mainImage: {
    width: '100%',
    height: 250,
  },
  imageOverlay: {
    position: 'absolute',
    top: 12,
    right: 12,
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: 20,
    padding: 8,
  },
  thumbnailContainer: {
    marginTop: 12,
  },
  thumbnail: {
    marginRight: 8,
    borderRadius: 8,
    overflow: 'hidden',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  selectedThumbnail: {
    borderColor: colors.turquoise,
  },
  thumbnailImage: {
    width: 60,
    height: 60,
  },
  infoCard: {
    margin: ResponsivePadding.horizontal,
    marginTop: 16,
    elevation: theme.elevation.small,
  },
  titleRow: {
    marginBottom: 12,
  },
  itemTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 8,
  },
  statusChips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  statusChip: {
    borderRadius: 16,
  },
  priorityChip: {
    borderRadius: 16,
  },
  chipText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  description: {
    fontSize: 16,
    lineHeight: 24,
    color: theme.colors.onSurface,
    marginBottom: 12,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  tag: {
    backgroundColor: theme.colors.grey200,
    height: 28,
  },
  tagText: {
    fontSize: 12,
    color: theme.colors.text,
  },
  progressCard: {
    margin: ResponsivePadding.horizontal,
    marginTop: 16,
    elevation: theme.elevation.small,
  },
  priceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  priceLabel: {
    fontSize: 16,
    color: theme.colors.text,
  },
  price: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.turquoise,
  },
  progressInfo: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  progressItem: {
    alignItems: 'center',
  },
  progressValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.success,
  },
  progressLabel: {
    fontSize: 12,
    color: theme.colors.disabled,
    marginTop: 4,
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
    marginBottom: 8,
  },
  progressText: {
    textAlign: 'center',
    fontSize: 14,
    fontWeight: 'bold',
    color: colors.turquoise,
  },
  contributorsCard: {
    margin: ResponsivePadding.horizontal,
    marginTop: 16,
    elevation: theme.elevation.small,
  },
  contributorsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  contributorsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
    color: theme.colors.text,
  },
  noContributors: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  noContributorsText: {
    marginTop: 12,
    textAlign: 'center',
    color: theme.colors.disabled,
    fontSize: 16,
  },
  contributorsList: {
    gap: 12,
  },
  contributorItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: theme.colors.grey50,
    borderRadius: 8,
  },
  contributorAvatar: {
    backgroundColor: colors.turquoise,
  },
  contributorInfo: {
    flex: 1,
    marginLeft: 12,
  },
  contributorName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  contributorAmount: {
    fontSize: 14,
    color: colors.success,
    fontWeight: 'bold',
  },
  contributorMessage: {
    fontSize: 12,
    color: theme.colors.disabled,
    marginTop: 2,
  },
  contributorDate: {
    fontSize: 12,
    color: theme.colors.disabled,
  },
  moreContributors: {
    padding: 12,
    alignItems: 'center',
  },
  moreContributorsText: {
    color: colors.turquoise,
    fontWeight: 'bold',
  },
  actionsCard: {
    margin: ResponsivePadding.horizontal,
    marginTop: 16,
    marginBottom: 100,
    elevation: theme.elevation.small,
  },
  actionsContainer: {
    gap: 12,
    marginBottom: 16,
  },
  contributeButton: {
    borderRadius: 8,
  },
  linkButton: {
    borderRadius: 8,
    borderColor: colors.turquoise,
  },
  shareButton: {
    borderRadius: 8,
    borderColor: colors.turquoise,
  },
  buttonContent: {
    paddingVertical: 8,
  },
  dateText: {
    fontSize: 12,
    color: theme.colors.disabled,
    textAlign: 'center',
  },
  dialog: {
    borderRadius: 16,
  },
  dialogTitle: {
    textAlign: 'center',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  dialogInput: {
    marginBottom: 16,
  },
  anonymousContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  anonymousLabel: {
    fontSize: 16,
    color: theme.colors.text,
  },
  remainingInfo: {
    padding: 12,
    borderRadius: 8,
    backgroundColor: colors.mintLight + '40',
  },
  remainingInfoText: {
    fontSize: 14,
    color: theme.colors.text,
    textAlign: 'center',
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
});
