import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Alert,
  Linking,
  Platform,
  SafeAreaView,
} from 'react-native';
import {
  Card,
  Text,
  TextInput,
  Button,
  RadioButton,
  Divider,
  Switch,
  Portal,
  Dialog,
  ActivityIndicator,
} from 'react-native-paper';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useRoute } from '@react-navigation/native';

import theme from '../utils/theme';
import PaymentService from '../services/paymentService';
import ResponsiveLayout, { ResponsivePadding } from '../components/common/ResponsiveLayout';

const PaymentScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const { type, itemId, itemTitle, suggestedAmount } = route.params as any;

  const [amount, setAmount] = useState(suggestedAmount?.toString() || '');
  const [description, setDescription] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('zarinpal');
  const [loading, setLoading] = useState(false);
  const [confirmDialog, setConfirmDialog] = useState(false);

  useEffect(() => {
    if (type === 'contribution' && itemTitle) {
      setDescription(`کمک به ${itemTitle}`);
    } else if (type === 'wallet_charge') {
      setDescription('شارژ کیف پول');
    }
  }, [type, itemTitle]);

  const predefinedAmounts = [10000, 25000, 50000, 100000, 250000, 500000];

  const handlePayment = async () => {
    if (!amount || parseFloat(amount) <= 0) {
      Alert.alert('خطا', 'لطفاً مبلغ معتبری وارد کنید');
      return;
    }

    setConfirmDialog(true);
  };

  const confirmPayment = async () => {
    setConfirmDialog(false);
    setLoading(true);

    try {
      let paymentResponse;
      const amountValue = parseFloat(amount);

      if (type === 'contribution' && itemId) {
        paymentResponse = await PaymentService.contributeToWishlistItem(
          itemId,
          amountValue,
          isAnonymous
        );
      } else if (type === 'wallet_charge') {
        paymentResponse = await PaymentService.chargeWallet(amountValue);
      }

      if (paymentResponse?.authority) {
        const paymentUrl = PaymentService.getPaymentUrl(paymentResponse.authority);
        
        // باز کردن صفحه پرداخت در مرورگر
        const canOpen = await Linking.canOpenURL(paymentUrl);
        if (canOpen) {
          await Linking.openURL(paymentUrl);
          
          // نمایش پیام به کاربر
          Alert.alert(
            'انتقال به درگاه پرداخت',
            'پس از تکمیل پرداخت، به اپلیکیشن برگردید',
            [
              {
                text: 'متوجه شدم',
                onPress: () => navigation.goBack(),
              },
            ]
          );
        } else {
          throw new Error('امکان باز کردن درگاه پرداخت وجود ندارد');
        }
      }
    } catch (error: any) {
      Alert.alert('خطا', error.message || 'خطا در انجام پرداخت');
    } finally {
      setLoading(false);
    }
  };

  const formatAmount = (value: string) => {
    const numericValue = value.replace(/[^0-9]/g, '');
    return PaymentService.formatAmount(parseInt(numericValue) || 0);
  };

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient
        colors={[theme.colors.primary, theme.colors.accent]}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <Ionicons
            name="card-outline"
            size={32}
            color={theme.colors.white}
          />
          <Text style={styles.headerTitle}>
            {type === 'contribution' ? 'کمک مالی' : 'شارژ کیف پول'}
          </Text>
          <Text style={styles.headerSubtitle}>
            {type === 'contribution' && itemTitle ? itemTitle : 'پرداخت امن'}
          </Text>
        </View>
      </LinearGradient>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <ResponsiveLayout>
          <View style={{ paddingHorizontal: ResponsivePadding.horizontal, paddingVertical: ResponsivePadding.vertical }}>
            
            {/* مبالغ پیشنهادی */}
            <Card style={styles.card}>
              <Card.Content>
                <Text style={styles.sectionTitle}>مبالغ پیشنهادی</Text>
                <View style={styles.amountGrid}>
                  {predefinedAmounts.map((amt) => (
                    <Button
                      key={amt}
                      mode={amount === amt.toString() ? 'contained' : 'outlined'}
                      onPress={() => setAmount(amt.toString())}
                      style={styles.amountButton}
                      labelStyle={styles.amountLabel}
                    >
                      {PaymentService.formatAmount(amt)} تومان
                    </Button>
                  ))}
                </View>
              </Card.Content>
            </Card>

            {/* مبلغ دلخواه */}
            <Card style={styles.card}>
              <Card.Content>
                <Text style={styles.sectionTitle}>مبلغ دلخواه</Text>
                <TextInput
                  mode="outlined"
                  label="مبلغ (تومان)"
                  value={amount ? formatAmount(amount) : ''}
                  onChangeText={(text) => setAmount(text.replace(/[^0-9]/g, ''))}
                  keyboardType="numeric"
                  right={<TextInput.Affix text="تومان" />}
                  style={styles.input}
                />
                
                {parseFloat(amount) > 0 && (
                  <View style={styles.amountInfo}>
                    <Text style={styles.convertedAmount}>
                      معادل: {PaymentService.formatAmount(parseFloat(amount) * 10)} ریال
                    </Text>
                  </View>
                )}
              </Card.Content>
            </Card>

            {/* تنظیمات کمک */}
            {type === 'contribution' && (
              <Card style={styles.card}>
                <Card.Content>
                  <Text style={styles.sectionTitle}>تنظیمات کمک</Text>
                  
                  <View style={styles.switchRow}>
                    <Text style={styles.switchLabel}>کمک ناشناس</Text>
                    <Switch
                      value={isAnonymous}
                      onValueChange={setIsAnonymous}
                    />
                  </View>
                  
                  <Text style={styles.switchDescription}>
                    {isAnonymous
                      ? 'نام شما برای صاحب لیست آرزو نمایش داده نخواهد شد'
                      : 'نام شما برای صاحب لیست آرزو نمایش داده خواهد شد'
                    }
                  </Text>
                </Card.Content>
              </Card>
            )}

            {/* روش پرداخت */}
            <Card style={styles.card}>
              <Card.Content>
                <Text style={styles.sectionTitle}>روش پرداخت</Text>
                
                <RadioButton.Group
                  onValueChange={setPaymentMethod}
                  value={paymentMethod}
                >
                  <View style={styles.paymentMethod}>
                    <RadioButton value="zarinpal" />
                    <Ionicons
                      name="card"
                      size={24}
                      color={theme.colors.primary}
                      style={styles.paymentIcon}
                    />
                    <View style={styles.paymentInfo}>
                      <Text style={styles.paymentName}>زرین‌پال</Text>
                      <Text style={styles.paymentDesc}>پرداخت آنلاین با کارت</Text>
                    </View>
                  </View>
                </RadioButton.Group>
              </Card.Content>
            </Card>

            {/* خلاصه پرداخت */}
            <Card style={styles.summaryCard}>
              <Card.Content>
                <Text style={styles.summaryTitle}>خلاصه پرداخت</Text>
                <Divider style={styles.divider} />
                
                <View style={styles.summaryRow}>
                  <Text style={styles.summaryLabel}>مبلغ:</Text>
                  <Text style={styles.summaryValue}>
                    {amount ? `${formatAmount(amount)} تومان` : '0 تومان'}
                  </Text>
                </View>
                
                <View style={styles.summaryRow}>
                  <Text style={styles.summaryLabel}>نوع پرداخت:</Text>
                  <Text style={styles.summaryValue}>
                    {type === 'contribution' ? 'کمک مالی' : 'شارژ کیف پول'}
                  </Text>
                </View>
                
                {type === 'contribution' && (
                  <View style={styles.summaryRow}>
                    <Text style={styles.summaryLabel}>حالت:</Text>
                    <Text style={styles.summaryValue}>
                      {isAnonymous ? 'ناشناس' : 'با نام'}
                    </Text>
                  </View>
                )}
                
                <Divider style={styles.divider} />
                
                <View style={styles.totalRow}>
                  <Text style={styles.totalLabel}>مبلغ قابل پرداخت:</Text>
                  <Text style={styles.totalValue}>
                    {amount ? `${formatAmount(amount)} تومان` : '0 تومان'}
                  </Text>
                </View>
              </Card.Content>
            </Card>

            {/* دکمه پرداخت */}
            <Button
              mode="contained"
              onPress={handlePayment}
              disabled={!amount || parseFloat(amount) <= 0 || loading}
              style={styles.payButton}
              contentStyle={styles.payButtonContent}
              labelStyle={styles.payButtonLabel}
              loading={loading}
            >
              {loading ? 'در حال انتقال...' : 'پرداخت'}
            </Button>

          </View>
        </ResponsiveLayout>
      </ScrollView>

      {/* دیالوگ تایید */}
      <Portal>
        <Dialog visible={confirmDialog} onDismiss={() => setConfirmDialog(false)}>
          <Dialog.Title>تایید پرداخت</Dialog.Title>
          <Dialog.Content>
            <Text style={styles.confirmText}>
              آیا از انجام پرداخت به مبلغ {amount ? formatAmount(amount) : '0'} تومان اطمینان دارید؟
            </Text>
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setConfirmDialog(false)}>لغو</Button>
            <Button onPress={confirmPayment} mode="contained">تایید</Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>
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
  },
  content: {
    flex: 1,
    marginTop: -15,
  },
  card: {
    marginBottom: 16,
    elevation: 2,
  },
  sectionTitle: {
    ...theme.typography.h4,
    marginBottom: 16,
  },
  amountGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  amountButton: {
    minWidth: '30%',
    marginBottom: 8,
  },
  amountLabel: {
    fontSize: 12,
  },
  input: {
    marginBottom: 8,
  },
  amountInfo: {
    marginTop: 8,
  },
  convertedAmount: {
    ...theme.typography.small,
    color: theme.colors.grey600,
    textAlign: 'center',
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  switchLabel: {
    ...theme.typography.body,
  },
  switchDescription: {
    ...theme.typography.small,
    color: theme.colors.grey600,
  },
  paymentMethod: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  paymentIcon: {
    marginLeft: 8,
    marginRight: 12,
  },
  paymentInfo: {
    flex: 1,
  },
  paymentName: {
    ...theme.typography.body,
    fontWeight: 'bold',
  },
  paymentDesc: {
    ...theme.typography.small,
    color: theme.colors.grey600,
  },
  summaryCard: {
    marginBottom: 20,
    backgroundColor: theme.colors.grey50,
  },
  summaryTitle: {
    ...theme.typography.h4,
    marginBottom: 16,
    textAlign: 'center',
  },
  divider: {
    marginVertical: 12,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  summaryLabel: {
    ...theme.typography.body,
  },
  summaryValue: {
    ...theme.typography.body,
    fontWeight: 'bold',
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  totalLabel: {
    ...theme.typography.body,
    fontWeight: 'bold',
  },
  totalValue: {
    ...theme.typography.body,
    fontWeight: 'bold',
    color: theme.colors.primary,
    fontSize: 18,
  },
  payButton: {
    marginBottom: 20,
  },
  payButtonContent: {
    paddingVertical: 8,
  },
  payButtonLabel: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  confirmText: {
    ...theme.typography.body,
    textAlign: 'center',
  },
});

export default PaymentScreen; 