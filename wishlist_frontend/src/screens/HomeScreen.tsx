import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  StyleSheet,
  FlatList,
  Alert,
  RefreshControl,
  Dimensions,
  ScrollView,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  FAB,
  Text,
  ActivityIndicator,
  Surface,
  Chip,
  Searchbar,
  Avatar,
  Badge,
} from 'react-native-paper';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { LinearGradient } from 'expo-linear-gradient';
import { useAuth } from '../context/AuthContext';
import { wishlistAPI, userAPI } from '../services/api';
import { theme } from '../utils/theme';

const { width } = Dimensions.get('window');
const isTablet = width > 768;

interface Wishlist {
  id: number;
  title: string;
  description: string;
  owner: string;
  created_at: string;
  items_count?: number;
  total_price?: number;
  completed_percentage?: number;
  is_public?: boolean;
  occasion?: string;
}

interface UserStats {
  total_wishlists: number;
  total_items: number;
  total_contributions: number;
  wallet_balance: number;
}

export const HomeScreen = ({ navigation }: any) => {
  const [wishlists, setWishlists] = useState<Wishlist[]>([]);
  const [filteredWishlists, setFilteredWishlists] = useState<Wishlist[]>([]);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'public' | 'private'>('all');
  const { user } = useAuth();

  useEffect(() => {
    loadData();
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [])
  );

  useEffect(() => {
    filterWishlists();
  }, [wishlists, searchQuery, selectedFilter]);

  const loadData = async () => {
    try {
      const [wishlistsRes, statsRes] = await Promise.all([
        wishlistAPI.getWishlists(),
        userAPI.getProfile()
      ]);
      
      setWishlists(wishlistsRes.data.results || wishlistsRes.data);
      setUserStats({
        total_wishlists: statsRes.data.wishlist_count || 0,
        total_items: statsRes.data.total_items || 0,
        total_contributions: statsRes.data.total_contributions || 0,
        wallet_balance: statsRes.data.wallet_balance || 0,
      });
    } catch (error) {
      console.error('Error loading data:', error);
      Alert.alert('خطا', 'خطا در بارگذاری اطلاعات');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const filterWishlists = () => {
    let filtered = wishlists;

    // Apply search filter
    if (searchQuery.trim()) {
      filtered = filtered.filter(wishlist =>
        wishlist.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        wishlist.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply privacy filter
    if (selectedFilter !== 'all') {
      filtered = filtered.filter(wishlist =>
        selectedFilter === 'public' ? wishlist.is_public : !wishlist.is_public
      );
    }

    setFilteredWishlists(filtered);
  };

  const getCompletionColor = (percentage: number) => {
    if (percentage < 30) return theme.colors.error;
    if (percentage < 70) return '#FF9800';
    return theme.colors.primary;
  };

  const renderStatsCard = () => (
    <Surface style={styles.statsCard}>
      <LinearGradient
        colors={[theme.colors.primary, theme.colors.accent]}
        style={styles.gradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <View style={styles.userInfo}>
          <Avatar.Text
            size={60}
            label={user?.first_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
            style={styles.avatar}
          />
          <View style={styles.userDetails}>
            <Title style={styles.userTitle}>
              سلام {user?.first_name || user?.username}!
            </Title>
            <Text style={styles.walletText}>
              موجودی: {userStats?.wallet_balance?.toLocaleString() || 0} تومان
            </Text>
          </View>
        </View>
        
        <View style={styles.statsRow}>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{userStats?.total_wishlists || 0}</Text>
            <Text style={styles.statLabel}>لیست آرزو</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{userStats?.total_items || 0}</Text>
            <Text style={styles.statLabel}>آیتم</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{userStats?.total_contributions || 0}</Text>
            <Text style={styles.statLabel}>مشارکت</Text>
          </View>
        </View>
      </LinearGradient>
    </Surface>
  );

  const renderFilters = () => (
    <View style={styles.filtersContainer}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <Chip
          mode={selectedFilter === 'all' ? 'flat' : 'outlined'}
          selected={selectedFilter === 'all'}
          onPress={() => setSelectedFilter('all')}
          style={styles.filterChip}
        >
          همه
        </Chip>
        <Chip
          mode={selectedFilter === 'public' ? 'flat' : 'outlined'}
          selected={selectedFilter === 'public'}
          onPress={() => setSelectedFilter('public')}
          style={styles.filterChip}
        >
          عمومی
        </Chip>
        <Chip
          mode={selectedFilter === 'private' ? 'flat' : 'outlined'}
          selected={selectedFilter === 'private'}
          onPress={() => setSelectedFilter('private')}
          style={styles.filterChip}
        >
          خصوصی
        </Chip>
      </ScrollView>
    </View>
  );

  const renderWishlistItem = ({ item }: { item: Wishlist }) => (
    <Card 
      style={[
        styles.wishlistCard,
        isTablet && styles.wishlistCardTablet
      ]}
      onPress={() => navigation.navigate('ItemDetail', { 
        wishlistId: item.id,
      })}
    >
      <Card.Content>
        <View style={styles.wishlistHeader}>
          <Title style={styles.wishlistTitle}>{item.title}</Title>
          <View style={styles.wishlistBadges}>
            {item.is_public && (
              <Badge style={styles.publicBadge}>عمومی</Badge>
            )}
          </View>
        </View>
        
        <Paragraph style={styles.wishlistDescription}>
          {item.description || 'بدون توضیحات'}
        </Paragraph>

        {item.occasion && (
          <View style={styles.occasionContainer}>
            <Ionicons name="calendar" size={16} color={theme.colors.primary} />
            <Text style={styles.occasionText}>{item.occasion}</Text>
          </View>
        )}

        <View style={styles.wishlistStats}>
          <View style={styles.statItem}>
            <Ionicons name="list" size={16} color={theme.colors.disabled} />
            <Text style={styles.statText}>{item.items_count || 0} آیتم</Text>
          </View>
          
          {item.total_price && (
            <View style={styles.statItem}>
              <Ionicons name="cash" size={16} color={theme.colors.disabled} />
              <Text style={styles.statText}>
                {item.total_price.toLocaleString()} تومان
              </Text>
            </View>
          )}
        </View>

        {item.completed_percentage !== undefined && (
          <View style={styles.progressContainer}>
            <View style={styles.progressBar}>
              <View 
                style={[
                  styles.progressFill,
                  { 
                    width: `${item.completed_percentage}%`,
                    backgroundColor: getCompletionColor(item.completed_percentage)
                  }
                ]}
              />
            </View>
            <Text style={styles.progressText}>
              {item.completed_percentage}% تکمیل شده
            </Text>
          </View>
        )}

        <Text style={styles.dateText}>
          {new Date(item.created_at).toLocaleDateString('fa-IR')}
        </Text>
      </Card.Content>
    </Card>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
        <Text style={styles.loadingText}>در حال بارگذاری...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Stats Card */}
      {renderStatsCard()}

      {/* Search Bar */}
      <Searchbar
        placeholder="جستجو در لیست آرزوها..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchBar}
      />

      {/* Filters */}
      {renderFilters()}

      {/* Wishlists */}
      {filteredWishlists.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="gift-outline" size={64} color={theme.colors.disabled} />
          <Text style={styles.emptyTitle}>
            {searchQuery || selectedFilter !== 'all' 
              ? 'هیچ لیست آرزویی یافت نشد'
              : 'هنوز لیست آرزویی ندارید'
            }
          </Text>
          <Text style={styles.emptyMessage}>
            {searchQuery || selectedFilter !== 'all'
              ? 'فیلترهای خود را تغییر دهید یا جستجوی جدیدی انجام دهید'
              : 'اولین لیست آرزوی خود را ایجاد کنید'
            }
          </Text>
          {!searchQuery && selectedFilter === 'all' && (
            <Button
              mode="contained"
              onPress={() => navigation.navigate('CreateWishlist')}
              style={styles.emptyButton}
              icon="plus"
            >
              ایجاد لیست آرزو
            </Button>
          )}
        </View>
      ) : (
        <FlatList
          data={filteredWishlists}
          renderItem={renderWishlistItem}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.listContainer}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          numColumns={isTablet ? 2 : 1}
          showsVerticalScrollIndicator={false}
        />
      )}

      {/* FAB */}
      <FAB
        style={styles.fab}
        icon="plus"
        onPress={() => navigation.navigate('CreateWishlist')}
        label={isTablet ? 'لیست جدید' : undefined}
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
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: theme.colors.text,
  },
  statsCard: {
    margin: 16,
    borderRadius: 12,
    elevation: 4,
    overflow: 'hidden',
  },
  gradient: {
    padding: 20,
  },
  userInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  avatar: {
    backgroundColor: 'rgba(255,255,255,0.2)',
  },
  userDetails: {
    marginLeft: 16,
    flex: 1,
  },
  userTitle: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  walletText: {
    color: 'rgba(255,255,255,0.9)',
    fontSize: 14,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    color: 'white',
    fontSize: 24,
    fontWeight: 'bold',
  },
  statLabel: {
    color: 'rgba(255,255,255,0.9)',
    fontSize: 12,
    marginTop: 4,
  },
  searchBar: {
    margin: 16,
    marginTop: 0,
  },
  filtersContainer: {
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  filterChip: {
    marginRight: 8,
  },
  listContainer: {
    padding: 16,
    paddingTop: 0,
  },
  wishlistCard: {
    marginBottom: 12,
    elevation: 3,
    borderRadius: 12,
  },
  wishlistCardTablet: {
    width: (width - 48) / 2,
    marginHorizontal: 4,
  },
  wishlistHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  wishlistTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    flex: 1,
  },
  wishlistBadges: {
    flexDirection: 'row',
  },
  publicBadge: {
    backgroundColor: theme.colors.primary,
    fontSize: 10,
  },
  wishlistDescription: {
    color: theme.colors.disabled,
    marginBottom: 12,
    lineHeight: 20,
  },
  occasionContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  occasionText: {
    marginLeft: 6,
    color: theme.colors.primary,
    fontSize: 14,
    fontWeight: '500',
  },
  wishlistStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  statText: {
    marginLeft: 4,
    color: theme.colors.disabled,
    fontSize: 14,
  },
  progressContainer: {
    marginBottom: 12,
  },
  progressBar: {
    height: 4,
    backgroundColor: theme.colors.disabled + '30',
    borderRadius: 2,
    marginBottom: 4,
  },
  progressFill: {
    height: '100%',
    borderRadius: 2,
  },
  progressText: {
    fontSize: 12,
    color: theme.colors.disabled,
  },
  dateText: {
    fontSize: 12,
    color: theme.colors.disabled,
    textAlign: 'left',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    textAlign: 'center',
    marginTop: 16,
    marginBottom: 8,
    color: theme.colors.text,
  },
  emptyMessage: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 24,
    color: theme.colors.disabled,
    lineHeight: 24,
  },
  emptyButton: {
    paddingHorizontal: 32,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: theme.colors.primary,
  },
});
