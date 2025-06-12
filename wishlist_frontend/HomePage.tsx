import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Platform,
  StyleSheet,
  Animated,
  Easing,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

const { width, height } = Dimensions.get('window');

// Comprehensive Responsive Breakpoints
const getDeviceType = () => {
  if (width < 480) return 'mobile-small';    // iPhone SE, small Android
  if (width < 768) return 'mobile';          // Most phones
  if (width < 1024) return 'tablet';         // iPad, Android tablets
  if (width < 1440) return 'desktop';        // Small desktops, laptops
  return 'desktop-large';                    // Large screens, 4K
};

const deviceType = getDeviceType();
const isMobileSmall = deviceType === 'mobile-small';
const isMobile = deviceType === 'mobile' || isMobileSmall;
const isTablet = deviceType === 'tablet';
const isDesktop = deviceType === 'desktop' || deviceType === 'desktop-large';
const isDesktopLarge = deviceType === 'desktop-large';

// Responsive sizing functions
const responsiveSize = {
  // Fonts
  heroTitle: isMobileSmall ? 28 : isMobile ? 34 : isTablet ? 42 : isDesktop ? 48 : 56,
  heroSubtitle: isMobileSmall ? 16 : isMobile ? 18 : isTablet ? 20 : isDesktop ? 22 : 26,
  sectionTitle: isMobileSmall ? 22 : isMobile ? 26 : isTablet ? 30 : isDesktop ? 34 : 40,
  cardTitle: isMobileSmall ? 16 : isMobile ? 18 : isTablet ? 20 : isDesktop ? 22 : 24,
  bodyText: isMobileSmall ? 13 : isMobile ? 14 : isTablet ? 16 : isDesktop ? 17 : 18,

  // Spacing
  sectionPadding: isMobileSmall ? 15 : isMobile ? 20 : isTablet ? 30 : isDesktop ? 40 : 50,
  cardPadding: isMobileSmall ? 15 : isMobile ? 20 : isTablet ? 25 : isDesktop ? 30 : 35,
  cardGap: isMobileSmall ? 15 : isMobile ? 20 : isTablet ? 25 : isDesktop ? 30 : 35,

  // Heights
  heroHeight: height * (isMobileSmall ? 0.85 : isMobile ? 0.9 : isTablet ? 0.85 : 0.8),
  cardHeight: isMobileSmall ? 140 : isMobile ? 160 : isTablet ? 180 : 200,
};

// Grid configurations
const getGridConfig = () => {
  if (isMobileSmall) return { columns: 1, statsColumns: 2 };
  if (isMobile) return { columns: 1, statsColumns: 2 };
  if (isTablet) return { columns: 2, statsColumns: 4 };
  if (isDesktop) return { columns: 2, statsColumns: 4 };
  return { columns: 3, statsColumns: 4 }; // Large desktop
};

const gridConfig = getGridConfig();

// Animated Preview Card Component
interface AnimatedPreviewCardProps {
  emoji: string;
  text: string;
  price: string;
  style: any;
  delay?: number;
}

const AnimatedPreviewCard: React.FC<AnimatedPreviewCardProps> = ({ emoji, text, price, style, delay = 0 }) => {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const translateYAnim = useRef(new Animated.Value(50)).current;
  const floatAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.6)).current;
  const rotateAnim = useRef(new Animated.Value(0)).current;
  const sparkleAnim = useRef(new Animated.Value(0)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    // Initial dramatic entrance animation
    const entranceAnimation = Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 1000,
        delay: delay * 1000,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
      Animated.timing(translateYAnim, {
        toValue: 0,
        duration: 1000,
        delay: delay * 1000,
        easing: Easing.out(Easing.back(1.8)),
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: 1000,
        delay: delay * 1000,
        easing: Easing.out(Easing.back(2)),
        useNativeDriver: true,
      }),
      Animated.timing(rotateAnim, {
        toValue: 1,
        duration: 1000,
        delay: delay * 1000,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
    ]);

    // Continuous floating animation
    const floatingAnimation = Animated.loop(
      Animated.sequence([
        Animated.timing(floatAnim, {
          toValue: -15,
          duration: 2500 + Math.random() * 1500,
          easing: Easing.inOut(Easing.sin),
          useNativeDriver: true,
        }),
        Animated.timing(floatAnim, {
          toValue: 15,
          duration: 2500 + Math.random() * 1500,
          easing: Easing.inOut(Easing.sin),
          useNativeDriver: true,
        }),
      ])
    );

    // Sparkle animation
    const sparkleAnimation = Animated.loop(
      Animated.timing(sparkleAnim, {
        toValue: 1,
        duration: 3000,
        easing: Easing.linear,
        useNativeDriver: true,
      })
    );

    // Pulse animation
    const pulseAnimation = Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.05,
          duration: 1500,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1500,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    );

    // Start animations
    entranceAnimation.start(() => {
      floatingAnimation.start();
      sparkleAnimation.start();
      pulseAnimation.start();
    });

    return () => {
      floatingAnimation.stop();
      sparkleAnimation.stop();
      pulseAnimation.stop();
    };
  }, []);

  const rotateInterpolation = rotateAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['-10deg', '0deg'],
  });

  const sparkleRotation = sparkleAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  const animatedStyle = {
    opacity: fadeAnim,
    transform: [
      { translateY: Animated.add(translateYAnim, floatAnim) },
      { scale: Animated.multiply(scaleAnim, pulseAnim) },
      { rotate: rotateInterpolation },
    ],
  };

  return (
    <Animated.View style={[styles.previewCard, style, animatedStyle]}>
      {/* Sparkle Effect */}
      <Animated.View style={[styles.sparkleContainer, { transform: [{ rotate: sparkleRotation }] }]}>
        <Text style={styles.sparkleText}>✨</Text>
      </Animated.View>

      {/* Main Content */}
      <View style={styles.cardContent}>
        <Text style={styles.previewCardEmoji}>{emoji}</Text>
        <Text style={styles.previewCardText}>{text}</Text>
        <Text style={styles.previewCardPrice}>{price}</Text>
      </View>

      {/* Glow Effect */}
      <View style={styles.cardGlow} />
    </Animated.View>
  );
};

interface HomePageProps {
  onNavigateToLogin: () => void;
}

export default function HomePage({ onNavigateToLogin }: HomePageProps) {
  const [activeFeature, setActiveFeature] = useState(0);

  const features = [
    {
      icon: '🎯',
      title: 'هوش مصنوعی پیشرفته',
      description: 'سیستم AI ما الگوهای خرید شما را تحلیل کرده و بهترین زمان، قیمت و فروشگاه را پیشنهاد می‌دهد',
      benefit: 'صرفه‌جویی تا 40% در هزینه‌ها'
    },
    {
      icon: '🌐',
      title: 'شبکه اجتماعی آرزوها',
      description: 'با میلیون‌ها کاربر در سراسر دنیا ارتباط برقرار کنید و در تحقق آرزوهای یکدیگر مشارکت کنید',
      benefit: 'دسترسی به شبکه جهانی کاربران'
    },
    {
      icon: '💎',
      title: 'سیستم پاداش‌دهی',
      description: 'با تحقق آرزوها و کمک به دیگران، امتیاز کسب کرده و جوایز ارزشمند دریافت کنید',
      benefit: 'درآمدزایی از طریق مشارکت'
    },
    {
      icon: '🔮',
      title: 'پیش‌بینی هوشمند',
      description: 'الگوریتم‌های پیشرفته ما احتمال تحقق آرزوهای شما را محاسبه کرده و راهکارهای بهینه ارائه می‌دهند',
      benefit: '85% دقت در پیش‌بینی موفقیت'
    },
    {
      icon: '🚀',
      title: 'تسریع‌گر آرزوها',
      description: 'ابزارهای انحصاری ما زمان تحقق آرزوهایتان را تا 60% کاهش می‌دهند',
      benefit: 'تحقق 3 برابر سریع‌تر آرزوها'
    },
    {
      icon: '🛡️',
      title: 'حفاظت کامل',
      description: 'سیستم امنیتی چندلایه و رمزگذاری بانکی برای محافظت کامل از اطلاعات و پرداخت‌های شما',
      benefit: 'امنیت در سطح بانکی'
    }
  ];

  const stats = [
    { number: '2.5M+', label: 'کاربر در سراسر جهان', icon: '🌍' },
    { number: '15M+', label: 'آرزوی ثبت شده', icon: '⭐' },
    { number: '8.2M+', label: 'آرزوی محقق شده', icon: '🎉' },
    { number: '$50M+', label: 'ارزش آرزوهای تحقق یافته', icon: '💰' }
  ];

  const testimonials = [
    {
      name: 'دکتر سارا محمدی',
      role: 'مدیرعامل استارتاپ تکنولوژی',
      text: 'این پلتفرم کاملاً زندگی‌ام رو تغییر داده! با هوش مصنوعی‌ش تونستم آرزوی ۵ سالم رو فقط در ۸ ماه محقق کنم. باورنکردنیه!',
      avatar: '👩‍💼',
      rating: 5,
      achievement: 'خرید خانه رویایی در تهران'
    },
    {
      name: 'محمدرضا کریمی',
      role: 'مهندس ارشد نرم‌افزار در گوگل',
      text: 'سیستم پیش‌بینی و تحلیل این پلتفرم واقعاً حرفه‌ای‌ترین چیزیه که تا حالا دیدم. الگوریتم‌هاش فوق‌العادن!',
      avatar: '👨‍💻',
      rating: 5,
      achievement: 'استقرار در سیلیکون ولی'
    },
    {
      name: 'پروفسور مریم احمدی',
      role: 'استاد دانشگاه شریف',
      text: 'از نظر علمی و فنی، این پلتفرم در سطح جهانی قرار داره. کمک‌کننده‌ترین ابزاری بوده که برای تحقق اهدافم استفاده کردم.',
      avatar: '👩‍🎓',
      rating: 5,
      achievement: 'انتشار کتاب بین‌المللی'
    }
  ];

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Hero Section */}
      <View style={styles.heroSection}>
        <LinearGradient
          colors={['#17A6A3', '#1B8B8A', '#136973']}
          style={styles.heroGradient}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
        >
          {/* Navigation */}
          <View style={styles.navigation}>
            <View style={styles.logoContainer}>
              <Text style={styles.logoIcon}>🎁</Text>
              <Text style={styles.logoText}>آرزوگرام</Text>
            </View>
            <TouchableOpacity
              style={styles.loginButton}
              onPress={onNavigateToLogin}
            >
              <Text style={styles.loginButtonText}>ورود</Text>
            </TouchableOpacity>
          </View>

          {/* Hero Content */}
          <View style={styles.heroContent}>
            <Text style={styles.heroTitle}>
              🌟 اولین پلتفرم هوش مصنوعی تحقق آرزوها در خاورمیانه
            </Text>
            <Text style={styles.heroSubtitle}>
              با قدرت AI پیشرفته و شبکه میلیونی کاربران، آرزوهایتان را 3 برابر سریع‌تر
              و با 40% صرفه‌جویی در هزینه محقق کنید
            </Text>

            <View style={styles.heroButtons}>
              <TouchableOpacity
                style={styles.primaryHeroButton}
                onPress={onNavigateToLogin}
              >
                <Text style={styles.primaryHeroButtonText}>🚀 شروع رایگان 30 روزه</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.secondaryHeroButton}
              >
                <Text style={styles.secondaryHeroButtonText}>📱 دانلود اپلیکیشن (iOS & Android)</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Preview Cards - Enhanced Floating examples */}
          <View style={styles.previewCards}>
            <AnimatedPreviewCard emoji="💎" text="خانه رویایی در تهران" price="۸ میلیارد تومان" style={styles.previewCard1} delay={0} />
            <AnimatedPreviewCard emoji="🚗" text="Tesla Model 3" price="۲ میلیارد تومان" style={styles.previewCard2} delay={0.3} />
            <AnimatedPreviewCard emoji="✈️" text="سفر به ژاپن" price="۵۰ میلیون تومان" style={styles.previewCard3} delay={0.6} />
            <AnimatedPreviewCard emoji="💰" text="کسب و کار شخصی" price="۱ میلیارد تومان" style={styles.previewCard4} delay={0.9} />
            <AnimatedPreviewCard emoji="🎓" text="تحصیل در آمریکا" price="۸۰۰ میلیون تومان" style={styles.previewCard5} delay={1.2} />
            <AnimatedPreviewCard emoji="💍" text="مراسم عروسی رویایی" price="۳۰۰ میلیون تومان" style={styles.previewCard6} delay={1.5} />
          </View>
        </LinearGradient>
      </View>

      {/* Stats Section */}
      <View style={styles.statsSection}>
        <Text style={styles.sectionTitle}>
          🏆 آمار جهانی پلتفرم در یک نگاه
        </Text>
        <Text style={styles.statsSubtitle}>
          میلیون‌ها کاربر در سراسر دنیا به ما اعتماد کرده‌اند
        </Text>
        <View style={styles.statsGrid}>
          {stats.map((stat, index) => (
            <View key={index} style={styles.statCard}>
              <Text style={styles.statIcon}>{stat.icon}</Text>
              <Text style={styles.statNumber}>
                {stat.number}
              </Text>
              <Text style={styles.statLabel}>
                {stat.label}
              </Text>
            </View>
          ))}
        </View>
      </View>

      {/* Features Section */}
      <View style={styles.featuresSection}>
        <Text style={styles.sectionTitle}>
          ⚡ تکنولوژی انقلابی که زندگی را متحول می‌کند
        </Text>
        <Text style={styles.featuresSubtitle}>
          با قدرت هوش مصنوعی و الگوریتم‌های پیشرفته، تجربه‌ای بی‌نظیر از تحقق آرزوها
        </Text>

        <View style={styles.featuresGrid}>
          {features.map((feature, index) => (
            <TouchableOpacity
              key={index}
              style={[
                styles.featureCard,
                activeFeature === index && styles.featureCardActive
              ]}
              onPress={() => setActiveFeature(index)}
            >
              <View style={styles.featureIcon}>
                <Text style={styles.featureIconText}>{feature.icon}</Text>
              </View>
              <View style={styles.featureContent}>
                <Text style={styles.featureTitle}>
                  {feature.title}
                </Text>
                <Text style={styles.featureDescription}>
                  {feature.description}
                </Text>
                <View style={styles.featureBenefit}>
                  <Text style={styles.featureBenefitIcon}>⚡</Text>
                  <Text style={styles.featureBenefitText}>{feature.benefit}</Text>
                </View>
              </View>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* How It Works Section */}
      <View style={styles.howItWorksSection}>
        <Text style={styles.sectionTitle}>
          🎯 مسیر هوشمند تحقق آرزوها در 4 گام ساده
        </Text>
        <Text style={styles.howItWorksSubtitle}>
          الگوریتم‌های پیشرفته ما مسیر بهینه را برای شما ترسیم می‌کنند
        </Text>
        <View style={styles.stepsContainer}>
          {[
            { step: 1, icon: '🎯', title: 'ثبت هوشمند آرزو', desc: 'AI ما بهترین راه‌حل را پیشنهاد می‌دهد' },
            { step: 2, icon: '🌐', title: 'اتصال به شبکه جهانی', desc: 'با میلیون‌ها کاربر ارتباط برقرار کنید' },
            { step: 3, icon: '��', title: 'تسریع با قدرت AI', desc: 'سیستم ما مسیر را بهینه‌سازی می‌کند' },
            { step: 4, icon: '🎉', title: 'تحقق تضمینی', desc: '85% احتمال موفقیت با الگوریتم ما' }
          ].map((item, index) => (
            <View key={index} style={styles.stepCard}>
              <View style={styles.stepNumber}>
                <Text style={styles.stepNumberText}>{item.step}</Text>
              </View>
              <Text style={styles.stepIcon}>{item.icon}</Text>
              <Text style={styles.stepTitle}>
                {item.title}
              </Text>
              <Text style={styles.stepDesc}>
                {item.desc}
              </Text>
              {index < 3 && (
                <View style={styles.stepArrow}>
                  <Text style={styles.stepArrowText}>→</Text>
                </View>
              )}
            </View>
          ))}
        </View>
      </View>

      {/* Testimonials Section */}
      <View style={styles.testimonialsSection}>
        <Text style={styles.sectionTitle}>
          💎 شهادت رهبران صنعت و اساتید برجسته
        </Text>
        <Text style={styles.testimonialsSubtitle}>
          موفق‌ترین افراد جامعه تجربه خود را با شما به اشتراک می‌گذارند
        </Text>
        <View style={styles.testimonialsGrid}>
          {testimonials.map((testimonial, index) => (
            <View key={index} style={styles.testimonialCard}>
              <Text style={styles.testimonialQuote}>"</Text>
              <View style={styles.testimonialRating}>
                {[...Array(testimonial.rating)].map((_, i) => (
                  <Text key={i} style={styles.star}>⭐</Text>
                ))}
              </View>
              <Text style={styles.testimonialText}>
                {testimonial.text}
              </Text>
              <View style={styles.testimonialAchievement}>
                <Text style={styles.achievementIcon}>🏆</Text>
                <Text style={styles.achievementText}>{testimonial.achievement}</Text>
              </View>
              <View style={styles.testimonialAuthor}>
                <Text style={styles.testimonialAvatar}>{testimonial.avatar}</Text>
                <View>
                  <Text style={styles.testimonialName}>{testimonial.name}</Text>
                  <Text style={styles.testimonialRole}>{testimonial.role}</Text>
                </View>
              </View>
            </View>
          ))}
        </View>
      </View>

      {/* CTA Section */}
      <View style={styles.ctaSection}>
        <LinearGradient
          colors={['#17A6A3', '#1B8B8A', '#136973']}
          style={styles.ctaGradient}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
        >
          <Text style={styles.ctaTitle}>
            🌟 آماده انقلاب در زندگی‌تان هستید؟
          </Text>
          <Text style={styles.ctaSubtitle}>
            به جمع 2.5 میلیون کاربر موفق بپیوندید و اولین آرزوی خود را با قدرت هوش مصنوعی محقق کنید
          </Text>
          <TouchableOpacity
            style={styles.ctaButton}
            onPress={onNavigateToLogin}
          >
            <Text style={styles.ctaButtonText}>🚀 شروع انقلاب شخصی</Text>
          </TouchableOpacity>
          <Text style={styles.ctaNote}>
            ⭐ 30 روز رایگان • بدون تعهد • لغو آسان • پشتیبانی 24/7
          </Text>
        </LinearGradient>
      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <View style={styles.footerContent}>
          <View style={styles.footerSection}>
            <Text style={styles.footerTitle}>درباره ما</Text>
            <Text style={styles.footerLink}>تیم ما</Text>
            <Text style={styles.footerLink}>داستان ما</Text>
            <Text style={styles.footerLink}>فرصت‌های شغلی</Text>
          </View>
          <View style={styles.footerSection}>
            <Text style={styles.footerTitle}>خدمات</Text>
            <Text style={styles.footerLink}>پلتفرم هوش مصنوعی</Text>
            <Text style={styles.footerLink}>مشاوره شخصی</Text>
            <Text style={styles.footerLink}>برنامه‌ریزی مالی</Text>
          </View>
          <View style={styles.footerSection}>
            <Text style={styles.footerTitle}>پشتیبانی</Text>
            <Text style={styles.footerLink}>راهنمای کاربری</Text>
            <Text style={styles.footerLink}>سوالات متداول</Text>
            <Text style={styles.footerLink}>تماس با ما</Text>
          </View>
          <View style={styles.footerSection}>
            <Text style={styles.footerTitle}>قوانین</Text>
            <Text style={styles.footerLink}>حریم خصوصی</Text>
            <Text style={styles.footerLink}>شرایط استفاده</Text>
            <Text style={styles.footerLink}>قوانین امنیت</Text>
          </View>
        </View>
        <View style={styles.footerBottom}>
          <Text style={styles.footerCopyright}>
            © 2024 پلتفرم هوش مصنوعی تحقق آرزوها. تمامی حقوق محفوظ است.
          </Text>
          <Text style={styles.footerNote}>
            🚀 ساخته شده با عشق در ایران • پیشرفته‌ترین تکنولوژی AI
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },

  // Hero Section - Responsive
  heroSection: {
    height: responsiveSize.heroHeight,
    position: 'relative',
    overflow: 'hidden',
  },
  heroSectionDesktop: {
    height: responsiveSize.heroHeight,
  },
  heroGradient: {
    flex: 1,
    backgroundColor: '#17A6A3',
    borderBottomLeftRadius: isMobileSmall ? 30 : isMobile ? 40 : 50,
    borderBottomRightRadius: isMobileSmall ? 30 : isMobile ? 40 : 50,
    overflow: 'hidden',
    position: 'relative',
  },

  // Navigation - Responsive
  navigation: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: responsiveSize.sectionPadding,
    paddingTop: isMobileSmall ? 40 : isMobile ? 50 : isTablet ? 50 : 60,
    paddingBottom: isMobileSmall ? 20 : isMobile ? 25 : 30,
    position: 'relative',
    zIndex: 100,
  },
  navigationDesktop: {
    paddingHorizontal: '8%',
    paddingTop: 30,
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    paddingHorizontal: isMobileSmall ? 15 : isMobile ? 18 : 20,
    paddingVertical: isMobileSmall ? 8 : isMobile ? 10 : 12,
    borderRadius: isMobileSmall ? 20 : isMobile ? 22 : 25,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 8,
  },
  logoIcon: {
    fontSize: isMobileSmall ? 24 : isMobile ? 28 : isTablet ? 32 : 36,
    marginRight: isMobileSmall ? 8 : isMobile ? 10 : 12,
  },
  logoText: {
    fontSize: isMobileSmall ? 18 : isMobile ? 22 : isTablet ? 26 : 26,
    fontWeight: 'bold',
    color: 'white',
    letterSpacing: 0.8,
  },
  logoTextDesktop: {
    fontSize: 28,
  },
  loginButton: {
    backgroundColor: 'white',
    paddingHorizontal: isMobileSmall ? 18 : isMobile ? 22 : isTablet ? 28 : 35,
    paddingVertical: isMobileSmall ? 10 : isMobile ? 12 : isTablet ? 16 : 18,
    borderRadius: isMobileSmall ? 20 : isMobile ? 25 : 30,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.25,
    shadowRadius: 12,
    elevation: 10,
    borderWidth: 1,
    borderColor: 'rgba(23, 166, 163, 0.1)',
  },
  loginButtonDesktop: {
    paddingHorizontal: 30,
    paddingVertical: 15,
  },
  loginButtonText: {
    color: '#17A6A3',
    fontSize: isMobileSmall ? 13 : isMobile ? 14 : isTablet ? 16 : 16,
    fontWeight: 'bold',
    letterSpacing: 0.5,
  },

  // Hero Content - Responsive
  heroContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: responsiveSize.sectionPadding,
    paddingBottom: isMobileSmall ? 80 : isMobile ? 100 : isTablet ? 110 : 120,
    position: 'relative',
    zIndex: 50,
  },
  heroContentDesktop: {
    paddingHorizontal: '15%',
  },
  heroTitle: {
    fontSize: responsiveSize.heroTitle,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    marginBottom: isMobileSmall ? 15 : isMobile ? 20 : 25,
    letterSpacing: isMobileSmall ? 0.8 : isMobile ? 1.0 : 1.2,
    lineHeight: responsiveSize.heroTitle * 1.3,
    maxWidth: isDesktop ? '90%' : '100%',
  },
  heroTitleDesktop: {
    fontSize: responsiveSize.heroTitle,
    lineHeight: 64,
  },
  heroSubtitle: {
    fontSize: responsiveSize.heroSubtitle,
    color: 'rgba(255, 255, 255, 0.95)',
    textAlign: 'center',
    lineHeight: responsiveSize.heroSubtitle * 1.6,
    marginBottom: isMobileSmall ? 30 : isMobile ? 35 : isTablet ? 40 : 45,
    letterSpacing: isMobileSmall ? 0.3 : isMobile ? 0.4 : 0.6,
    fontWeight: '400',
    maxWidth: isMobileSmall ? '100%' : isMobile ? '95%' : isTablet ? '85%' : 700,
  },
  heroSubtitleDesktop: {
    fontSize: responsiveSize.heroSubtitle,
    lineHeight: 34,
    marginBottom: 50,
  },

  // Hero Buttons - Responsive
  heroButtons: {
    width: '100%',
    gap: isMobileSmall ? 15 : isMobile ? 18 : 20,
    maxWidth: isMobileSmall ? 300 : isMobile ? 400 : isTablet ? 500 : 600,
    flexDirection: isDesktop ? 'row' : 'column',
    justifyContent: isDesktop ? 'center' : 'flex-start',
  },
  heroButtonsDesktop: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 25,
    width: 'auto',
  },
  heroButtonDesktop: {
    minWidth: 200,
  },
  primaryHeroButton: {
    backgroundColor: 'white',
    paddingVertical: isMobileSmall ? 16 : isMobile ? 18 : 20,
    paddingHorizontal: isDesktop ? 30 : 20,
    borderRadius: isMobileSmall ? 25 : isMobile ? 30 : 35,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 20,
    elevation: 15,
    borderWidth: 3,
    borderColor: 'rgba(255, 255, 255, 0.3)',
    position: 'relative',
    overflow: 'hidden',
    minWidth: isDesktop ? 250 : 'auto',
  },
  primaryHeroButtonText: {
    color: '#17A6A3',
    fontSize: isMobileSmall ? 16 : isMobile ? 18 : 20,
    fontWeight: 'bold',
    textAlign: 'center',
    letterSpacing: 0.8,
    textTransform: 'uppercase',
  },
  secondaryHeroButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    paddingVertical: isMobileSmall ? 16 : isMobile ? 18 : 20,
    paddingHorizontal: isDesktop ? 30 : 20,
    borderRadius: isMobileSmall ? 25 : isMobile ? 30 : 35,
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.4)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 8,
    minWidth: isDesktop ? 250 : 'auto',
  },
  secondaryHeroButtonText: {
    color: 'white',
    fontSize: isMobileSmall ? 16 : isMobile ? 18 : 20,
    fontWeight: '600',
    textAlign: 'center',
    letterSpacing: 0.8,
  },

  // Preview Cards - Responsive
  previewCards: {
    position: 'absolute',
    bottom: isMobileSmall ? -30 : isMobile ? -35 : -40,
    left: 0,
    right: 0,
    height: isMobileSmall ? 80 : isMobile ? 100 : 120,
    zIndex: 40,
  },
  previewCardsDesktop: {
    bottom: -40,
    height: 120,
  },
  previewCard: {
    position: 'absolute',
    backgroundColor: 'white',
    borderRadius: isMobileSmall ? 15 : isMobile ? 20 : 25,
    padding: isMobileSmall ? 10 : isMobile ? 15 : 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.25,
    shadowRadius: 20,
    elevation: 15,
    flexDirection: 'row',
    alignItems: 'center',
    gap: isMobileSmall ? 8 : isMobile ? 12 : 15,
    borderWidth: 1,
    borderColor: 'rgba(23, 166, 163, 0.1)',
    maxWidth: isMobileSmall ? 140 : isMobile ? 160 : 200,
  },
  previewCard1: {
    left: responsiveSize.sectionPadding,
    top: isMobileSmall ? 15 : isMobile ? 20 : 25,
    transform: [{ rotate: '-3deg' }],
  },
  previewCard2: {
    right: responsiveSize.sectionPadding,
    top: isMobileSmall ? 5 : isMobile ? 5 : 5,
    transform: [{ rotate: '2deg' }],
  },
  previewCard3: {
    left: '35%',
    top: isMobileSmall ? 35 : isMobile ? 40 : 45,
    transform: [{ rotate: '-1deg' }],
  },
  previewCard4: {
    left: '35%',
    top: isMobileSmall ? 35 : isMobile ? 40 : 45,
    transform: [{ rotate: '-1deg' }],
  },
  previewCard5: {
    left: '35%',
    top: isMobileSmall ? 35 : isMobile ? 40 : 45,
    transform: [{ rotate: '-1deg' }],
  },
  previewCard6: {
    left: '35%',
    top: isMobileSmall ? 35 : isMobile ? 40 : 45,
    transform: [{ rotate: '-1deg' }],
  },
  previewCardEmoji: {
    fontSize: isMobileSmall ? 24 : isMobile ? 28 : 32,
  },
  previewCardText: {
    fontSize: isMobileSmall ? 12 : isMobile ? 14 : 16,
    fontWeight: 'bold',
    color: '#043E50',
    letterSpacing: 0.5,
  },
  previewCardPrice: {
    fontSize: isMobileSmall ? 10 : isMobile ? 12 : 14,
    color: '#17A6A3',
    fontWeight: 'bold',
    textAlign: 'right',
    letterSpacing: 0.3,
  },
  sparkleContainer: {
    position: 'absolute',
    top: -5,
    right: -5,
    width: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
  },
  sparkleText: {
    fontSize: 16,
    textAlign: 'center',
  },
  cardContent: {
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 5,
  },
  cardGlow: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    borderRadius: isMobileSmall ? 15 : isMobile ? 18 : 20,
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: 'rgba(23, 166, 163, 0.3)',
    zIndex: 1,
  },

  // Stats Section - Responsive
  statsSection: {
    paddingHorizontal: responsiveSize.sectionPadding,
    paddingVertical: isMobileSmall ? 60 : isMobile ? 80 : isTablet ? 100 : 120,
    backgroundColor: '#FAFAFA',
    position: 'relative',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: isMobileSmall ? 'space-between' : isMobile ? 'space-around' : 'center',
    gap: responsiveSize.cardGap,
  },
  statCard: {
    alignItems: 'center',
    backgroundColor: 'white',
    borderRadius: isMobileSmall ? 20 : isMobile ? 25 : 30,
    padding: responsiveSize.cardPadding,
    minWidth: isMobileSmall ? (width - (responsiveSize.sectionPadding * 2) - responsiveSize.cardGap) / 2 :
      isMobile ? 140 :
        isTablet ? 160 : 180,
    minHeight: responsiveSize.cardHeight,
    shadowColor: '#17A6A3',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.12,
    shadowRadius: 25,
    elevation: 12,
    borderWidth: 1,
    borderColor: 'rgba(167, 215, 197, 0.2)',
    position: 'relative',
    overflow: 'hidden',
  },
  statIcon: {
    fontSize: isMobileSmall ? 32 : isMobile ? 40 : isTablet ? 44 : 48,
    marginBottom: isMobileSmall ? 8 : isMobile ? 12 : 15,
  },
  statNumber: {
    fontSize: isMobileSmall ? 20 : isMobile ? 24 : isTablet ? 30 : 36,
    fontWeight: 'bold',
    color: '#17A6A3',
    marginBottom: isMobileSmall ? 4 : isMobile ? 6 : 8,
    letterSpacing: 0.5,
  },
  statLabel: {
    fontSize: isMobileSmall ? 11 : isMobile ? 13 : isTablet ? 16 : 18,
    color: '#136973',
    textAlign: 'center',
    fontWeight: '600',
    letterSpacing: 0.3,
    lineHeight: isMobileSmall ? 16 : isMobile ? 18 : 22,
  },

  // Features Section - Responsive
  featuresSection: {
    paddingHorizontal: responsiveSize.sectionPadding,
    paddingVertical: isMobileSmall ? 50 : isMobile ? 70 : isTablet ? 90 : 100,
    backgroundColor: '#F8FFFE',
    position: 'relative',
  },
  featuresGrid: {
    gap: responsiveSize.cardGap,
    flexDirection: isDesktop ? 'row' : 'column',
    flexWrap: isDesktop ? 'wrap' : 'nowrap',
    justifyContent: isDesktop ? 'space-between' : 'flex-start',
  },
  featureCard: {
    backgroundColor: 'white',
    borderRadius: isMobileSmall ? 20 : isMobile ? 25 : 30,
    padding: responsiveSize.cardPadding,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.08,
    shadowRadius: 30,
    elevation: 10,
    borderWidth: 2,
    borderColor: 'transparent',
    position: 'relative',
    overflow: 'hidden',
    width: isDesktop ? '48%' : '100%',
  },
  featureCardActive: {
    borderColor: '#17A6A3',
    transform: [{ scale: 1.02 }],
    backgroundColor: '#F8FFFE',
    shadowOpacity: 0.15,
  },
  featureIcon: {
    width: isMobileSmall ? 60 : isMobile ? 70 : 80,
    height: isMobileSmall ? 60 : isMobile ? 70 : 80,
    borderRadius: isMobileSmall ? 30 : isMobile ? 35 : 40,
    backgroundColor: '#A7D7C5',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: isMobileSmall ? 15 : isMobile ? 20 : 25,
    shadowColor: '#17A6A3',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 8,
    borderWidth: 3,
    borderColor: 'rgba(255, 255, 255, 0.8)',
  },
  featureIconText: {
    fontSize: isMobileSmall ? 24 : isMobile ? 30 : 36,
  },
  featureContent: {
    gap: isMobileSmall ? 10 : isMobile ? 12 : 15,
  },
  featureTitle: {
    fontSize: responsiveSize.cardTitle,
    fontWeight: 'bold',
    color: '#043E50',
    lineHeight: responsiveSize.cardTitle * 1.4,
    textAlign: 'right',
    marginBottom: 5,
    letterSpacing: 0.5,
  },
  featureDescription: {
    fontSize: responsiveSize.bodyText,
    color: '#136973',
    lineHeight: responsiveSize.bodyText * 1.6,
    textAlign: 'right',
    fontWeight: '400',
    letterSpacing: 0.2,
  },
  featureBenefit: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    backgroundColor: 'rgba(23, 166, 163, 0.08)',
    padding: isMobileSmall ? 10 : isMobile ? 12 : 15,
    borderRadius: isMobileSmall ? 10 : isMobile ? 12 : 15,
    marginTop: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#17A6A3',
  },
  featureBenefitIcon: {
    fontSize: isMobileSmall ? 14 : isMobile ? 16 : 18,
  },
  featureBenefitText: {
    fontSize: isMobileSmall ? 10 : isMobile ? 11 : 13,
    color: '#17A6A3',
    fontWeight: 'bold',
    letterSpacing: 0.3,
    textTransform: 'uppercase',
  },

  // How It Works Section - Responsive
  howItWorksSection: {
    paddingHorizontal: responsiveSize.sectionPadding,
    paddingVertical: isMobileSmall ? 50 : isMobile ? 70 : isTablet ? 90 : 100,
    backgroundColor: '#F8FFFE',
    position: 'relative',
  },
  stepsContainer: {
    gap: responsiveSize.cardGap,
    flexDirection: isDesktop ? 'row' : 'column',
    justifyContent: isDesktop ? 'space-between' : 'flex-start',
    alignItems: isDesktop ? 'flex-start' : 'center',
  },
  stepCard: {
    backgroundColor: 'white',
    borderRadius: isMobileSmall ? 20 : isMobile ? 25 : 30,
    padding: responsiveSize.cardPadding,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.1,
    shadowRadius: 20,
    elevation: 10,
    alignItems: 'center',
    position: 'relative',
    borderWidth: 2,
    borderColor: 'rgba(23, 166, 163, 0.1)',
    width: isDesktop ? '22%' : '90%',
    minHeight: isMobileSmall ? 180 : isMobile ? 200 : 220,
  },
  stepNumber: {
    width: isMobileSmall ? 40 : isMobile ? 50 : 60,
    height: isMobileSmall ? 40 : isMobile ? 50 : 60,
    borderRadius: isMobileSmall ? 20 : isMobile ? 25 : 30,
    backgroundColor: '#17A6A3',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: isMobileSmall ? 15 : isMobile ? 20 : 25,
    shadowColor: '#17A6A3',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  stepNumberText: {
    fontSize: isMobileSmall ? 18 : isMobile ? 22 : 26,
    fontWeight: 'bold',
    color: 'white',
  },
  stepIcon: {
    fontSize: isMobileSmall ? 28 : isMobile ? 32 : 36,
    marginBottom: isMobileSmall ? 10 : isMobile ? 15 : 20,
  },
  stepTitle: {
    fontSize: responsiveSize.cardTitle,
    fontWeight: 'bold',
    color: '#043E50',
    textAlign: 'center',
    marginBottom: isMobileSmall ? 8 : isMobile ? 10 : 12,
    letterSpacing: 0.5,
  },
  stepDesc: {
    fontSize: responsiveSize.bodyText,
    color: '#136973',
    textAlign: 'center',
    lineHeight: responsiveSize.bodyText * 1.5,
    letterSpacing: 0.2,
  },
  stepArrow: {
    position: 'absolute',
    right: isDesktop ? -30 : 'auto',
    top: isDesktop ? '50%' : 'auto',
    bottom: isDesktop ? 'auto' : -25,
    left: isDesktop ? 'auto' : '50%',
    transform: isDesktop ? [{ translateY: -10 }] : [{ translateX: -10 }, { rotate: '90deg' }],
  },
  stepArrowText: {
    fontSize: isMobileSmall ? 24 : isMobile ? 28 : 32,
    color: '#A7D7C5',
    fontWeight: 'bold',
  },

  // Testimonials Section - Responsive
  testimonialsSection: {
    paddingHorizontal: responsiveSize.sectionPadding,
    paddingVertical: isMobileSmall ? 50 : isMobile ? 70 : isTablet ? 90 : 100,
    backgroundColor: '#E6F7F6',
    position: 'relative',
  },
  testimonialsGrid: {
    gap: responsiveSize.cardGap,
    flexDirection: isDesktop ? 'row' : 'column',
  },
  testimonialCard: {
    backgroundColor: 'white',
    borderRadius: isMobileSmall ? 20 : isMobile ? 25 : 30,
    padding: responsiveSize.cardPadding,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 15 },
    shadowOpacity: 0.08,
    shadowRadius: 35,
    elevation: 12,
    position: 'relative',
    borderWidth: 1,
    borderColor: 'rgba(167, 215, 197, 0.3)',
    flex: isDesktop ? 1 : 0,
  },
  testimonialQuote: {
    fontSize: isMobileSmall ? 40 : isMobile ? 50 : 60,
    color: '#A7D7C5',
    position: 'absolute',
    top: 15,
    right: 25,
    lineHeight: isMobileSmall ? 40 : isMobile ? 50 : 60,
    fontWeight: 'bold',
  },
  testimonialRating: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 15,
    gap: 2,
  },
  star: {
    fontSize: isMobileSmall ? 14 : isMobile ? 16 : 18,
  },
  testimonialText: {
    fontSize: responsiveSize.bodyText,
    color: '#136973',
    lineHeight: responsiveSize.bodyText * 1.6,
    marginTop: 25,
    marginBottom: 25,
    textAlign: 'right',
    fontWeight: '400',
    letterSpacing: 0.3,
    fontStyle: 'italic',
  },
  testimonialAchievement: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F0F9FF',
    padding: isMobileSmall ? 8 : isMobile ? 10 : 12,
    borderRadius: isMobileSmall ? 8 : isMobile ? 10 : 12,
    marginBottom: 15,
    alignSelf: 'flex-start',
  },
  testimonialAuthor: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 15,
    borderTopWidth: 1,
    borderTopColor: 'rgba(167, 215, 197, 0.3)',
    paddingTop: 20,
  },
  testimonialAvatar: {
    fontSize: isMobileSmall ? 32 : isMobile ? 36 : 40,
    backgroundColor: '#F8FFFE',
    borderRadius: isMobileSmall ? 25 : isMobile ? 30 : 35,
    width: isMobileSmall ? 50 : isMobile ? 60 : 70,
    height: isMobileSmall ? 50 : isMobile ? 60 : 70,
    textAlign: 'center',
    lineHeight: isMobileSmall ? 50 : isMobile ? 60 : 70,
    borderWidth: 2,
    borderColor: '#A7D7C5',
  },
  testimonialName: {
    fontSize: responsiveSize.bodyText,
    fontWeight: 'bold',
    color: '#043E50',
    marginBottom: 4,
    letterSpacing: 0.3,
  },
  testimonialRole: {
    fontSize: isMobileSmall ? 12 : isMobile ? 13 : 14,
    color: '#136973',
    fontWeight: '500',
  },

  // CTA Section - Responsive
  ctaSection: {
    marginHorizontal: responsiveSize.sectionPadding,
    marginVertical: isMobileSmall ? 50 : isMobile ? 70 : isTablet ? 80 : 100,
    borderRadius: isMobileSmall ? 25 : isMobile ? 35 : 40,
    overflow: 'hidden',
    position: 'relative',
  },
  ctaGradient: {
    backgroundColor: '#17A6A3',
    padding: isMobileSmall ? 30 : isMobile ? 40 : 50,
    alignItems: 'center',
    position: 'relative',
  },
  ctaTitle: {
    fontSize: isMobileSmall ? 22 : isMobile ? 26 : isTablet ? 32 : 36,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    marginBottom: isMobileSmall ? 15 : isMobile ? 18 : 20,
    letterSpacing: 0.8,
  },
  ctaSubtitle: {
    fontSize: responsiveSize.bodyText,
    color: 'rgba(255, 255, 255, 0.95)',
    textAlign: 'center',
    marginBottom: isMobileSmall ? 30 : isMobile ? 35 : 40,
    lineHeight: responsiveSize.bodyText * 1.6,
    letterSpacing: 0.4,
    maxWidth: isMobileSmall ? '100%' : isTablet ? 500 : 600,
  },
  ctaButton: {
    backgroundColor: 'white',
    paddingVertical: isMobileSmall ? 18 : isMobile ? 20 : 25,
    paddingHorizontal: isMobileSmall ? 40 : isMobile ? 50 : 60,
    borderRadius: isMobileSmall ? 25 : isMobile ? 30 : 35,
    marginBottom: isMobileSmall ? 20 : isMobile ? 22 : 25,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.3,
    shadowRadius: 20,
    elevation: 15,
    borderWidth: 3,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  ctaButtonText: {
    color: '#17A6A3',
    fontSize: isMobileSmall ? 16 : isMobile ? 18 : 20,
    fontWeight: 'bold',
    textAlign: 'center',
    letterSpacing: 0.8,
    textTransform: 'uppercase',
  },
  ctaNote: {
    fontSize: isMobileSmall ? 13 : isMobile ? 14 : 16,
    color: 'rgba(255, 255, 255, 0.9)',
    textAlign: 'center',
    letterSpacing: 0.3,
    fontWeight: '500',
  },

  // Footer - Responsive
  footer: {
    backgroundColor: '#136973',
    paddingHorizontal: responsiveSize.sectionPadding,
    paddingVertical: isMobileSmall ? 40 : isMobile ? 50 : 60,
  },
  footerContent: {
    flexDirection: isDesktop ? 'row' : 'column',
    justifyContent: isDesktop ? 'space-between' : 'flex-start',
    gap: responsiveSize.cardGap,
    marginBottom: isMobileSmall ? 30 : isMobile ? 40 : 50,
  },
  footerSection: {
    alignItems: isDesktop ? 'flex-start' : 'center',
    marginBottom: isMobileSmall ? 20 : isMobile ? 25 : 0,
    flex: isDesktop ? 1 : 0,
  },
  footerTitle: {
    fontSize: responsiveSize.cardTitle,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: isMobileSmall ? 8 : isMobile ? 10 : 12,
    textAlign: isDesktop ? 'right' : 'center',
  },
  footerLink: {
    fontSize: responsiveSize.bodyText,
    color: 'rgba(255, 255, 255, 0.9)',
    marginBottom: isMobileSmall ? 6 : isMobile ? 8 : 10,
    textAlign: isDesktop ? 'right' : 'center',
  },
  footerBottom: {
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 255, 255, 0.2)',
    paddingTop: isMobileSmall ? 20 : isMobile ? 25 : 30,
  },
  footerCopyright: {
    fontSize: responsiveSize.bodyText,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
    marginBottom: isMobileSmall ? 8 : isMobile ? 10 : 12,
  },
  footerNote: {
    fontSize: isMobileSmall ? 12 : isMobile ? 13 : 14,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
  },

  // Section Titles and Subtitles - Responsive
  sectionTitle: {
    fontSize: responsiveSize.sectionTitle,
    fontWeight: 'bold',
    color: '#043E50',
    textAlign: 'center',
    marginBottom: isMobileSmall ? 30 : isMobile ? 40 : 50,
    letterSpacing: 1,
    lineHeight: responsiveSize.sectionTitle * 1.3,
    position: 'relative',
  },
  statsSubtitle: {
    fontSize: responsiveSize.bodyText,
    color: '#136973',
    textAlign: 'center',
    lineHeight: responsiveSize.bodyText * 1.5,
    marginBottom: isMobileSmall ? 30 : isMobile ? 35 : 40,
    letterSpacing: 0.3,
    fontWeight: '500',
  },
  featuresSubtitle: {
    fontSize: responsiveSize.bodyText,
    color: '#136973',
    textAlign: 'center',
    lineHeight: responsiveSize.bodyText * 1.5,
    marginBottom: isMobileSmall ? 30 : isMobile ? 35 : 40,
    letterSpacing: 0.3,
    fontWeight: '500',
  },
  howItWorksSubtitle: {
    fontSize: responsiveSize.bodyText,
    color: '#136973',
    textAlign: 'center',
    lineHeight: responsiveSize.bodyText * 1.5,
    marginBottom: isMobileSmall ? 30 : isMobile ? 35 : 40,
    letterSpacing: 0.3,
    fontWeight: '500',
  },
  testimonialsSubtitle: {
    fontSize: responsiveSize.bodyText,
    color: '#136973',
    textAlign: 'center',
    lineHeight: responsiveSize.bodyText * 1.5,
    marginBottom: isMobileSmall ? 30 : isMobile ? 35 : 40,
    letterSpacing: 0.3,
    fontWeight: '500',
  },
  achievementIcon: {
    fontSize: isMobileSmall ? 16 : isMobile ? 18 : 20,
    marginRight: isMobileSmall ? 6 : isMobile ? 8 : 10,
  },
  achievementText: {
    fontSize: isMobileSmall ? 10 : isMobile ? 11 : 12,
    color: '#17A6A3',
    fontWeight: 'bold',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
}); 