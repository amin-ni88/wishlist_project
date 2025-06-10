import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  FlatList,
  Alert,
  RefreshControl,
} from 'react-native';
import {
  Card,
  Title,
  Text,
  Button,
  Surface,
  ActivityIndicator,
  Chip,
  Divider,
  FAB,
} from 'react-native-paper';
import { Ionicons } from '@expo/vector-icons';
import { userAPI } from '../../services/api';
import { theme } from '../../utils/theme';

interface WalletScreenProps {
  navigation: any;
}

interface Transaction {
  id: number;
  amount: number;
  type: 'CHARGE' | 'CONTRIBUTION' | 'PURCHASE';
  description: string;
  created_at: string;
  status: 'PENDING' | 'COMPLETED' | 'FAILED';
}

const WalletScreen: React.FC<WalletScreenProps> = ({ navigation }) => {
  const [balance, setBalance] = useState(0);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchWalletData();
  }, []);

  const fetchWalletData = async () => {
    try {
      const [profileRes, transactionsRes] = await Promise.all([
        userAPI.getProfile(),
        userAPI.getTransactions(),
      ]);
      
      setBalance(profileRes.data.wallet_balance || 0);
      setTransactions(transactionsRes.data.results || []);
    } catch (error) {
      console.error('Error fetching wallet data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchWalletData();
  };

  const handleCharge = () => {
    Alert.alert(
      'شارژ کیف پول',
      'برای شارژ کیف پول به درگاه پرداخت منتقل می‌شوید.',
      [
        { text: 'لغو', style: 'cancel' },
        { text: 'ادامه', onPress: () => {
          // Navigate to payment gateway or show charge modal
          Alert.alert('در حال توسعه', 'این قابلیت به زودی اضافه خواهد شد.');
        }},
      ]
    );
  };

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'CHARGE':
        return 'arrow-down-circle';
      case 'CONTRIBUTION':
        return 'gift';
      case 'PURCHASE':
        return 'bag';
      default:
        return 'swap-horizontal';
    }
  };

  const getTransactionColor = (type: string) => {
    switch (type) {
      case 'CHARGE':
        return theme.colors.primary;
      case 'CONTRIBUTION':
        return theme.colors.secondary;
      case 'PURCHASE':
        return theme.colors.accent;
      default:
        return theme.colors.disabled;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return theme.colors.primary;
      case 'PENDING':
        return '#FF9800';
      case 'FAILED':
        return theme.colors.error;
      default:
        return theme.colors.disabled;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'موفق';
      case 'PENDING':
        return 'در انتظار';
      case 'FAILED':
        return 'ناموفق';
      default:
        return 'نامشخص';
    }
  };

  const renderTransaction = ({ item }: { item: Transaction }) => (
    <Card style={styles.transactionCard}>
      <Card.Content>
        <View style={styles.transactionHeader}>
          <View style={styles.transactionLeft}>
            <Ionicons
              name={getTransactionIcon(item.type)}
              size={24}
              color={getTransactionColor(item.type)}
            />
            <View style={styles.transactionInfo}>
              <Text style={styles.transactionDescription}>{item.description}</Text>
              <Text style={styles.transactionDate}>
                {new Date(item.created_at).toLocaleDateString('fa-IR')}
              </Text>
            </View>
          </View>
          <View style={styles.transactionRight}>
            <Text style={[
              styles.transactionAmount,
              { color: item.type === 'CHARGE' ? theme.colors.primary : theme.colors.accent }
            ]}>
              {item.type === 'CHARGE' ? '+' : '-'}{item.amount.toLocaleString()} تومان
            </Text>
            <Chip
              style={[styles.statusChip, { backgroundColor: getStatusColor(item.status) }]}
              textStyle={styles.statusText}
            >
              {getStatusText(item.status)}
            </Chip>
          </View>
        </View>
      </Card.Content>
    </Card>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Balance Card */}
      <Surface style={styles.balanceCard}>
        <View style={styles.balanceHeader}>
          <Ionicons name="wallet" size={32} color={theme.colors.primary} />
          <View style={styles.balanceInfo}>
            <Text style={styles.balanceLabel}>موجودی کیف پول</Text>
            <Title style={styles.balanceAmount}>
              {balance.toLocaleString()} تومان
            </Title>
          </View>
        </View>
        <Button
          mode="contained"
          onPress={handleCharge}
          style={styles.chargeButton}
          icon="plus"
        >
          شارژ کیف پول
        </Button>
      </Surface>

      {/* Transactions List */}
      <View style={styles.transactionsContainer}>
        <Text style={styles.sectionTitle}>تاریخچه تراکنش‌ها</Text>
        <FlatList
          data={transactions}
          renderItem={renderTransaction}
          keyExtractor={(item) => item.id.toString()}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          showsVerticalScrollIndicator={false}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Ionicons name="receipt-outline" size={64} color={theme.colors.disabled} />
              <Text style={styles.emptyText}>هیچ تراکنشی یافت نشد</Text>
            </View>
          }
        />
      </View>

      {/* Quick Actions FAB */}
      <FAB
        style={styles.fab}
        icon="credit-card"
        onPress={handleCharge}
        label="شارژ سریع"
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
  balanceCard: {
    margin: 16,
    padding: 20,
    borderRadius: 12,
    elevation: 4,
  },
  balanceHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  balanceInfo: {
    marginLeft: 12,
    flex: 1,
  },
  balanceLabel: {
    fontSize: 14,
    color: theme.colors.disabled,
    marginBottom: 4,
  },
  balanceAmount: {
    fontSize: 28,
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
  chargeButton: {
    marginTop: 12,
  },
  transactionsContainer: {
    flex: 1,
    marginHorizontal: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
    color: theme.colors.text,
  },
  transactionCard: {
    marginBottom: 8,
    elevation: 2,
  },
  transactionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  transactionLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  transactionInfo: {
    marginLeft: 12,
    flex: 1,
  },
  transactionDescription: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 4,
  },
  transactionDate: {
    fontSize: 12,
    color: theme.colors.disabled,
  },
  transactionRight: {
    alignItems: 'flex-end',
  },
  transactionAmount: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  statusChip: {
    height: 24,
  },
  statusText: {
    fontSize: 10,
    color: 'white',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    marginTop: 16,
    fontSize: 16,
    color: theme.colors.disabled,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: theme.colors.primary,
  },
});

export default WalletScreen; 