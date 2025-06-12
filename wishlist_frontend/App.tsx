import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert, ScrollView, Dimensions, Platform } from 'react-native';

const { width, height } = Dimensions.get('window');
const isDesktop = width > 1024;
const isTablet = width > 768 && width <= 1024;
const isMobile = width <= 768;

// API Configuration
const API_BASE = 'http://127.0.0.1:8001';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [authMode, setAuthMode] = useState('username');
  const [formData, setFormData] = useState({
    username: '',
    phone: '',
    email: '',
    password: '',
    otp: '',
  });
  const [securityState, setSecurityState] = useState({
    isLoading: false,
    step: 1, // 1: login, 2: otp, 3: success
  });

  // Mock user info
  const userInfo = {
    username: formData.username || formData.phone || formData.email || 'کاربر',
    authMethod: authMode,
    loginTime: new Date().toLocaleString('fa-IR'),
  };

  // Handle Login
  const handleLogin = async () => {
    if (authMode === 'username' && (!formData.username || !formData.password)) {
      Alert.alert('خطا', 'لطفاً نام کاربری و رمز عبور را وارد کنید');
      return;
    }
    if (authMode === 'phone' && !formData.phone) {
      Alert.alert('خطا', 'لطفاً شماره موبایل را وارد کنید');
      return;
    }
    if (authMode === 'email' && !formData.email) {
      Alert.alert('خطا', 'لطفاً آدرس ایمیل را وارد کنید');
      return;
    }

    setSecurityState({ isLoading: true, step: 1 });
    
    // Simulate API call
    setTimeout(() => {
      setIsLoggedIn(true);
      setSecurityState({ isLoading: false, step: 3 });
      Alert.alert('موفقیت', 'ورود با موفقیت انجام شد');
    }, 1500);
  };

  // Handle Logout
  const handleLogout = () => {
    setIsLoggedIn(false);
    setFormData({
      username: '',
      phone: '',
      email: '',
      password: '',
      otp: '',
    });
    setSecurityState({ isLoading: false, step: 1 });
    setAuthMode('username');
  };

  // If logged in, show dashboard
  if (isLoggedIn) {
    return (
      <ScrollView style={styles.container}>
        {/* Enhanced Header */}
        <View style={[styles.header, isDesktop && styles.headerDesktop]}>
          <View style={styles.headerGradient}>
            <Text style={[styles.mainTitle, isDesktop && styles.mainTitleDesktop]}>
              ✨ پلتفرم لیست آرزوها
            </Text>
            <Text style={[styles.subtitle, isDesktop && styles.subtitleDesktop]}>
              خوش آمدید {userInfo.username}! 🎉
            </Text>
            
            {/* Beautiful Stats */}
            <View style={[styles.statsContainer, isDesktop && styles.statsDesktop]}>
              <View style={styles.statCard}>
                <Text style={styles.statNumber}>12</Text>
                <Text style={styles.statLabel}>آرزو</Text>
              </View>
              <View style={styles.statCard}>
                <Text style={styles.statNumber}>5</Text>
                <Text style={styles.statLabel}>تحقق شده</Text>
              </View>
              <View style={styles.statCard}>
                <Text style={styles.statNumber}>7</Text>
                <Text style={styles.statLabel}>در انتظار</Text>
              </View>
            </View>
          </View>
        </View>

        {/* Enhanced Features Section */}
        <View style={[styles.featuresContainer, isDesktop && styles.featuresDesktop]}>
          <Text style={[styles.sectionTitle, isDesktop && styles.sectionTitleDesktop]}>
            ✨ امکانات شگفت‌انگیز
          </Text>
          
          <View style={[styles.featuresGrid, isDesktop && styles.featuresGridDesktop]}>
            {[
              { icon: '🎁', title: 'لیست آرزوهای شخصی', desc: 'آرزوهای خود را ثبت و پیگیری کنید' },
              { icon: '👥', title: 'اشتراک‌گذاری جادویی', desc: 'لیست آرزوها را با دوستان به اشتراک بگذارید' },
              { icon: '💳', title: 'مشارکت در خرید', desc: 'دوستان در تحقق آرزوهای شما سهیم باشند' },
              { icon: '📊', title: 'آمار و گزارش کامل', desc: 'پیگیری هوشمند پیشرفت آرزوها' },
            ].map((feature, index) => (
              <View key={index} style={[styles.featureCard, isDesktop && styles.featureCardDesktop]}>
                <View style={styles.featureIcon}>
                  <Text style={styles.featureIconText}>{feature.icon}</Text>
                </View>
                <View style={styles.featureContent}>
                  <Text style={[styles.featureTitle, isDesktop && styles.featureTitleDesktop]}>
                    {feature.title}
                  </Text>
                  <Text style={[styles.featureDesc, isDesktop && styles.featureDescDesktop]}>
                    {feature.desc}
                  </Text>
                </View>
              </View>
            ))}
          </View>
        </View>

        {/* Enhanced Action Buttons */}
        <View style={[styles.actionContainer, isDesktop && styles.actionDesktop]}>
          <TouchableOpacity style={[styles.primaryButton, isDesktop && styles.buttonDesktop]}>
            <Text style={[styles.buttonText, styles.primaryButtonText]}>
              + ایجاد آرزوی جدید
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={[styles.secondaryButton, isDesktop && styles.buttonDesktop]}>
            <Text style={[styles.buttonText, styles.secondaryButtonText]}>
              📋 مشاهده همه آرزوها
            </Text>
          </TouchableOpacity>
        </View>

        {/* Logout Button */}
        <TouchableOpacity style={[styles.logoutButton, isDesktop && styles.buttonDesktop]} onPress={handleLogout}>
          <Text style={[styles.buttonText, styles.logoutButtonText]}>
            🚪 خروج از حساب
          </Text>
        </TouchableOpacity>
      </ScrollView>
    );
  }

  // Login Screen
  return (
    <View style={styles.container}>
      {/* Enhanced Login Background */}
      <View style={[styles.loginBackground, isDesktop && styles.loginBackgroundDesktop]}>
        <View style={styles.backgroundPattern} />
      </View>

      <ScrollView contentContainerStyle={[styles.loginContent, isDesktop && styles.loginContentDesktop]}>
        {/* Beautiful Logo Section */}
        <View style={styles.logoContainer}>
          <View style={[styles.logo, isDesktop && styles.logoDesktop]}>
            <Text style={[styles.logoText, isDesktop && styles.logoTextDesktop]}>🎁</Text>
          </View>
          <Text style={[styles.mainTitle, isDesktop && styles.mainTitleDesktop]}>
            پلتفرم لیست آرزوها
          </Text>
          <Text style={[styles.subtitle, isDesktop && styles.subtitleDesktop]}>
            آرزوهای خود را محقق کنید ✨
          </Text>
        </View>

        {/* Enhanced Login Card */}
        <View style={[styles.loginCard, isDesktop && styles.loginCardDesktop]}>
          {/* Beautiful Auth Mode Selector */}
          <View style={styles.authModeSelector}>
            {[
              { key: 'username', icon: '👤', label: 'نام کاربری' },
              { key: 'phone', icon: '📱', label: 'موبایل' },
              { key: 'email', icon: '📧', label: 'ایمیل' }
            ].map((mode) => (
              <TouchableOpacity
                key={mode.key}
                style={[styles.authModeTab, authMode === mode.key && styles.authModeTabActive]}
                onPress={() => setAuthMode(mode.key)}
              >
                <Text style={[
                  styles.authModeText, 
                  isDesktop && styles.authModeTextDesktop,
                  authMode === mode.key && styles.authModeTextActive
                ]}>
                  {mode.icon} {mode.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={[styles.cardTitle, isDesktop && styles.cardTitleDesktop]}>
            ورود امن به حساب کاربری
          </Text>
          <Text style={[styles.cardSubtitle, isDesktop && styles.cardSubtitleDesktop]}>
            {authMode === 'username' && 'نام کاربری و رمز عبور خود را وارد کنید'}
            {authMode === 'phone' && 'شماره موبایل خود را برای دریافت کد وارد کنید'}
            {authMode === 'email' && 'آدرس ایمیل خود را برای تایید وارد کنید'}
          </Text>

          {/* Enhanced Input Fields */}
          <View style={styles.inputContainer}>
            {authMode === 'username' && (
              <>
                <Text style={[styles.inputLabel, isDesktop && styles.inputLabelDesktop]}>
                  👤 نام کاربری
                </Text>
                <TextInput
                  style={[styles.input, isDesktop && styles.inputDesktop]}
                  placeholder="نام کاربری خود را وارد کنید"
                  value={formData.username}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, username: text }))}
                  placeholderTextColor="#A7D7C5"
                />
                <Text style={[styles.inputLabel, isDesktop && styles.inputLabelDesktop]}>
                  🔐 رمز عبور
                </Text>
                <TextInput
                  style={[styles.input, isDesktop && styles.inputDesktop]}
                  placeholder="رمز عبور امن خود را وارد کنید"
                  value={formData.password}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, password: text }))}
                  secureTextEntry
                  placeholderTextColor="#A7D7C5"
                />
              </>
            )}

            {authMode === 'phone' && (
              <>
                <Text style={[styles.inputLabel, isDesktop && styles.inputLabelDesktop]}>
                  📱 شماره موبایل
                </Text>
                <TextInput
                  style={[styles.input, isDesktop && styles.inputDesktop]}
                  placeholder="09xxxxxxxxx"
                  value={formData.phone}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, phone: text }))}
                  keyboardType="phone-pad"
                  placeholderTextColor="#A7D7C5"
                />
              </>
            )}

            {authMode === 'email' && (
              <>
                <Text style={[styles.inputLabel, isDesktop && styles.inputLabelDesktop]}>
                  📧 آدرس ایمیل
                </Text>
                <TextInput
                  style={[styles.input, isDesktop && styles.inputDesktop]}
                  placeholder="example@email.com"
                  value={formData.email}
                  onChangeText={(text) => setFormData(prev => ({ ...prev, email: text }))}
                  keyboardType="email-address"
                  placeholderTextColor="#A7D7C5"
                />
              </>
            )}
          </View>

          {/* Enhanced Login Button */}
          <TouchableOpacity 
            style={[
              styles.loginButton, 
              isDesktop && styles.buttonDesktop,
              securityState.isLoading && styles.buttonDisabled
            ]} 
            onPress={handleLogin}
            disabled={securityState.isLoading}
          >
            <Text style={[styles.buttonText, styles.primaryButtonText]}>
              {securityState.isLoading ? '⏳ در حال پردازش...' : '🚀 ورود به پلتفرم'}
            </Text>
          </TouchableOpacity>

          {/* Social Login */}
          <View style={styles.divider}>
            <View style={styles.dividerLine} />
            <Text style={[styles.dividerText, isDesktop && styles.dividerTextDesktop]}>یا</Text>
            <View style={styles.dividerLine} />
          </View>

          <TouchableOpacity style={[styles.googleButton, isDesktop && styles.buttonDesktop]}>
            <Text style={[styles.buttonText, styles.googleButtonText]}>
              🔗 ورود سریع با گوگل
            </Text>
          </TouchableOpacity>
        </View>

        {/* Enhanced Security Features */}
        <View style={[styles.securityFeatures, isDesktop && styles.securityDesktop]}>
          <Text style={[styles.cardTitle, isDesktop && styles.cardTitleDesktop]}>
            🛡️ امنیت پیشرفته
          </Text>
          <View style={styles.securityItems}>
            <Text style={[styles.securityItem, isDesktop && styles.securityItemDesktop]}>
              🔐 احراز هویت چندمرحله‌ای
            </Text>
            <Text style={[styles.securityItem, isDesktop && styles.securityItemDesktop]}>
              🤖 سیستم ضد ربات هوشمند
            </Text>
            <Text style={[styles.securityItem, isDesktop && styles.securityItemDesktop]}>
              📱 تایید دو مرحله‌ای
            </Text>
            <Text style={[styles.securityItem, isDesktop && styles.securityItemDesktop]}>
              🔒 رمزگذاری end-to-end
            </Text>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
  },

  // Enhanced Typography Styles
  mainTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    marginBottom: 10,
    letterSpacing: 0.8,
    lineHeight: 42,
    ...Platform.select({
      web: {
        textShadow: '0px 3px 6px rgba(0, 0, 0, 0.4)',
      },
      default: {
        textShadowColor: 'rgba(0, 0, 0, 0.4)',
        textShadowOffset: { width: 0, height: 3 },
        textShadowRadius: 6,
      },
    }),
  },
  mainTitleDesktop: {
    fontSize: 42,
    lineHeight: 56,
    letterSpacing: 1.2,
  },

  subtitle: {
    fontSize: 18,
    color: 'rgba(255, 255, 255, 0.95)',
    textAlign: 'center',
    letterSpacing: 0.4,
    lineHeight: 28,
    fontWeight: '400',
    fontStyle: 'italic',
    marginBottom: 20,
  },
  subtitleDesktop: {
    fontSize: 22,
    lineHeight: 32,
    marginBottom: 25,
  },

  cardTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#043E50',
    textAlign: 'center',
    marginBottom: 10,
    letterSpacing: 0.5,
    lineHeight: 28,
  },
  cardTitleDesktop: {
    fontSize: 24,
    lineHeight: 32,
    marginBottom: 12,
  },

  cardSubtitle: {
    fontSize: 16,
    color: '#136973',
    textAlign: 'center',
    marginBottom: 25,
    lineHeight: 24,
    fontWeight: '400',
  },
  cardSubtitleDesktop: {
    fontSize: 18,
    lineHeight: 28,
    marginBottom: 30,
  },

  sectionTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#043E50',
    marginBottom: 20,
    textAlign: 'center',
    letterSpacing: 0.5,
    lineHeight: 30,
  },
  sectionTitleDesktop: {
    fontSize: 28,
    lineHeight: 38,
    marginBottom: 25,
  },

  // Button Text Styles
  buttonText: {
    textAlign: 'center',
    fontWeight: 'bold',
    letterSpacing: 0.5,
  },
  primaryButtonText: {
    color: 'white',
    fontSize: 16,
    lineHeight: 22,
  },
  secondaryButtonText: {
    color: '#043E50',
    fontSize: 16,
    lineHeight: 22,
  },
  logoutButtonText: {
    color: '#136973',
    fontSize: 16,
    lineHeight: 22,
  },
  googleButtonText: {
    color: '#136973',
    fontSize: 14,
    lineHeight: 20,
  },

  // Input Styles
  inputLabel: {
    fontSize: 16,
    color: '#043E50',
    marginBottom: 8,
    fontWeight: '600',
    letterSpacing: 0.3,
    textAlign: 'right',
    lineHeight: 22,
  },
  inputLabelDesktop: {
    fontSize: 18,
    lineHeight: 26,
    marginBottom: 10,
  },

  input: {
    height: 55,
    borderWidth: 2.5,
    borderColor: '#A7D7C5',
    borderRadius: 15,
    paddingHorizontal: 18,
    fontSize: 16,
    backgroundColor: '#F8FFFE',
    textAlign: 'center',
    marginBottom: 18,
    lineHeight: 24,
  },
  inputDesktop: {
    height: 60,
    fontSize: 18,
    lineHeight: 28,
    marginBottom: 20,
  },

  // Layout Styles
  loginBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: height * 0.4,
    backgroundColor: '#17A6A3',
    borderBottomLeftRadius: 35,
    borderBottomRightRadius: 35,
  },
  loginBackgroundDesktop: {
    height: height * 0.35,
    borderBottomLeftRadius: 50,
    borderBottomRightRadius: 50,
  },
  backgroundPattern: {
    flex: 1,
    backgroundColor: 'rgba(167, 215, 197, 0.25)',
    borderBottomLeftRadius: 35,
    borderBottomRightRadius: 35,
  },

  loginContent: {
    flexGrow: 1,
    paddingHorizontal: 20,
    paddingTop: 70,
  },
  loginContentDesktop: {
    paddingHorizontal: '15%',
    paddingTop: 80,
  },

  logoContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logo: {
    width: 90,
    height: 90,
    borderRadius: 45,
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 25,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 15,
  },
  logoDesktop: {
    width: 120,
    height: 120,
    borderRadius: 60,
  },
  logoText: {
    fontSize: 50,
  },
  logoTextDesktop: {
    fontSize: 60,
  },

  loginCard: {
    backgroundColor: 'white',
    borderRadius: 25,
    padding: 30,
    marginBottom: 25,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.2,
    shadowRadius: 20,
    elevation: 15,
  },
  loginCardDesktop: {
    maxWidth: 550,
    alignSelf: 'center',
    padding: 40,
    borderRadius: 30,
  },

  authModeSelector: {
    flexDirection: 'row',
    backgroundColor: '#F8FFFE',
    borderRadius: 15,
    padding: 6,
    marginBottom: 25,
  },
  authModeTab: {
    flex: 1,
    paddingVertical: 15,
    borderRadius: 12,
    alignItems: 'center',
  },
  authModeTabActive: {
    backgroundColor: '#17A6A3',
    shadowColor: '#17A6A3',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 3,
  },
  authModeText: {
    fontSize: 12,
    color: '#136973',
    fontWeight: '600',
    textAlign: 'center',
    letterSpacing: 0.3,
  },
  authModeTextDesktop: {
    fontSize: 14,
  },
  authModeTextActive: {
    color: 'white',
    fontWeight: 'bold',
  },

  inputContainer: {
    marginBottom: 25,
  },

  // Button Styles
  loginButton: {
    backgroundColor: '#17A6A3',
    paddingVertical: 18,
    borderRadius: 15,
    marginBottom: 20,
    shadowColor: '#17A6A3',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 8,
  },
  buttonDesktop: {
    paddingVertical: 20,
  },
  buttonDisabled: {
    backgroundColor: '#A7D7C5',
    shadowOpacity: 0.1,
    elevation: 2,
  },

  googleButton: {
    backgroundColor: '#FFFFFF',
    borderWidth: 2.5,
    borderColor: '#A7D7C5',
    paddingVertical: 14,
    borderRadius: 15,
    marginBottom: 15,
  },

  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 25,
  },
  dividerLine: {
    flex: 1,
    height: 1.5,
    backgroundColor: '#A7D7C5',
  },
  dividerText: {
    marginHorizontal: 15,
    color: '#136973',
    fontSize: 14,
    fontWeight: '500',
  },
  dividerTextDesktop: {
    fontSize: 16,
  },

  // Dashboard Styles
  header: {
    height: 240,
    marginBottom: 25,
  },
  headerDesktop: {
    height: 280,
  },
  headerGradient: {
    flex: 1,
    backgroundColor: '#17A6A3',
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
    paddingHorizontal: 25,
    paddingTop: 60,
    justifyContent: 'center',
  },

  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 20,
  },
  statsDesktop: {
    justifyContent: 'center',
    gap: 40,
  },
  statCard: {
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.25)',
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderRadius: 15,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    letterSpacing: 0.5,
  },
  statLabel: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.9)',
    textAlign: 'center',
    fontWeight: '500',
    marginTop: 4,
  },

  // Features
  featuresContainer: {
    paddingHorizontal: 25,
    marginBottom: 25,
  },
  featuresDesktop: {
    paddingHorizontal: '8%',
  },
  featuresGrid: {},
  featuresGridDesktop: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  featureCard: {
    flexDirection: 'row',
    backgroundColor: 'white',
    borderRadius: 20,
    padding: 25,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.12,
    shadowRadius: 10,
    elevation: 5,
  },
  featureCardDesktop: {
    width: '48%',
    marginBottom: 20,
  },
  featureIcon: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#A7D7C5',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 20,
  },
  featureIconText: {
    fontSize: 28,
  },
  featureContent: {
    flex: 1,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#043E50',
    marginBottom: 8,
    letterSpacing: 0.3,
    lineHeight: 22,
    textAlign: 'right',
  },
  featureTitleDesktop: {
    fontSize: 18,
    lineHeight: 26,
  },
  featureDesc: {
    fontSize: 14,
    color: '#136973',
    lineHeight: 20,
    textAlign: 'right',
    fontWeight: '400',
  },
  featureDescDesktop: {
    fontSize: 16,
    lineHeight: 24,
  },

  // Actions
  actionContainer: {
    paddingHorizontal: 25,
    marginBottom: 25,
  },
  actionDesktop: {
    paddingHorizontal: '15%',
    flexDirection: 'row',
    gap: 25,
  },
  primaryButton: {
    backgroundColor: '#17A6A3',
    paddingVertical: 18,
    borderRadius: 15,
    marginBottom: 15,
    shadowColor: '#17A6A3',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 8,
  },
  secondaryButton: {
    backgroundColor: '#A7D7C5',
    paddingVertical: 18,
    borderRadius: 15,
  },

  logoutButton: {
    marginHorizontal: 25,
    paddingVertical: 16,
    borderWidth: 2.5,
    borderColor: '#136973',
    borderRadius: 15,
    marginBottom: 40,
  },

  // Security
  securityFeatures: {
    backgroundColor: 'white',
    borderRadius: 20,
    padding: 25,
    marginBottom: 40,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.12,
    shadowRadius: 10,
    elevation: 5,
  },
  securityDesktop: {
    maxWidth: 550,
    alignSelf: 'center',
  },
  securityItems: {
    alignItems: 'center',
    gap: 8,
  },
  securityItem: {
    fontSize: 14,
    color: '#136973',
    marginBottom: 12,
    textAlign: 'center',
    lineHeight: 20,
    fontWeight: '500',
  },
  securityItemDesktop: {
    fontSize: 16,
    lineHeight: 24,
  },
}); 