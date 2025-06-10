import { MD3LightTheme as DefaultTheme } from 'react-native-paper';
import { I18nManager } from 'react-native';
import { fontConfig, textStyles, fontFamily } from './fonts';

export const colors = {
  // پالت رنگی اصلی
  mintLight: '#A7D7C5',      // سبز-نعنایی روشن
  turquoise: '#17A6A3',      // فیروزه‌ای
  tealDark: '#136973',       // آبی تیره با ته‌مایه سبز
  navy: '#043E50',           // آبی نفتی
  darkBlue: '#082D45',       // سرمه‌ای تیره
  
  // رنگ‌های اضافی
  white: '#FFFFFF',
  black: '#000000',
  error: '#D32F2F',
  warning: '#FF9800',
  success: '#4CAF50',
  info: '#2196F3',
  
  // رنگ‌های خاکستری
  grey50: '#FAFAFA',
  grey100: '#F5F5F5',
  grey200: '#EEEEEE',
  grey300: '#E0E0E0',
  grey400: '#BDBDBD',
  grey500: '#9E9E9E',
  grey600: '#757575',
  grey700: '#616161',
  grey800: '#424242',
  grey900: '#212121',
};

export const theme = {
  ...DefaultTheme,
  isRTL: true,
  writingDirection: 'rtl' as const,
  colors: {
    ...DefaultTheme.colors,
    primary: colors.turquoise,           // #17A6A3 - فیروزه‌ای
    secondary: colors.mintLight,         // #A7D7C5 - سبز-نعنایی روشن
    accent: colors.tealDark,            // #136973 - آبی تیره با ته‌مایه سبز
    background: colors.grey50,          // #FAFAFA
    surface: colors.white,              // #FFFFFF
    error: colors.error,                // #D32F2F
    text: colors.darkBlue,              // #082D45 - سرمه‌ای تیره
    onSurface: colors.navy,             // #043E50 - آبی نفتی
    disabled: colors.grey500,           // #9E9E9E
    placeholder: colors.grey400,        // #BDBDBD
    backdrop: `${colors.darkBlue}80`,   // سرمه‌ای تیره با شفافیت
    notification: colors.turquoise,     // #17A6A3
    white: colors.white,
    black: colors.black,
    
    // رنگ‌های خاکستری
    grey50: colors.grey50,
    grey100: colors.grey100,
    grey200: colors.grey200,
    grey300: colors.grey300,
    grey400: colors.grey400,
    grey500: colors.grey500,
    grey600: colors.grey600,
    grey700: colors.grey700,
    grey800: colors.grey800,
    grey900: colors.grey900,
    
    // رنگ‌های اضافی برای gradient ها
    gradientStart: colors.turquoise,    // #17A6A3
    gradientEnd: colors.tealDark,       // #136973
    
    // رنگ‌های وضعیت
    success: colors.success,
    warning: colors.warning,
    info: colors.info,
  },
  roundness: 12,
  animation: {
    scale: 1.0,
  },
  typography: {
    h1: {
      ...textStyles.h1,
      color: colors.darkBlue,
    },
    h2: {
      ...textStyles.h2,
      color: colors.darkBlue,
    },
    h3: {
      ...textStyles.h3,
      color: colors.navy,
    },
    h4: {
      ...textStyles.h4,
      color: colors.navy,
    },
    body: {
      ...textStyles.body1,
      color: colors.navy,
    },
    body2: {
      ...textStyles.body2,
      color: colors.navy,
    },
    small: {
      ...textStyles.caption,
      color: colors.grey600,
    },
    caption: {
      ...textStyles.caption,
      color: colors.grey500,
    },
    button: {
      ...textStyles.button,
      color: colors.white,
    },
    label: {
      ...textStyles.label,
      color: colors.darkBlue,
    },
  },
  fonts: fontConfig.default,
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  elevation: {
    small: 2,
    medium: 4,
    large: 8,
    xlarge: 12,
  },
  shadows: {
    small: {
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 2,
    },
    medium: {
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.15,
      shadowRadius: 8,
      elevation: 4,
    },
    large: {
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.2,
      shadowRadius: 12,
      elevation: 8,
    },
  },
};

export default theme;
