// Persian Fonts Configuration for Wishlist App
// Using Vazir and Dana fonts for better Persian text rendering

export const fontFamily = {
  // فونت‌های اصلی
  primary: 'Vazir',           // فونت اصلی - وزیر
  secondary: 'Dana',          // فونت ثانویه - دانا
  english: 'System',          // فونت انگلیسی
  
  // وزن‌های مختلف وزیر
  vazir: {
    thin: 'Vazir-Thin',
    light: 'Vazir-Light',
    regular: 'Vazir',
    medium: 'Vazir-Medium',
    bold: 'Vazir-Bold',
    black: 'Vazir-Black',
  },
  
  // وزن‌های مختلف دانا
  dana: {
    thin: 'Dana-Thin',
    light: 'Dana-Light',
    regular: 'Dana',
    medium: 'Dana-Medium',
    demiBold: 'Dana-DemiBold',
    bold: 'Dana-Bold',
    extraBold: 'Dana-ExtraBold',
    black: 'Dana-Black',
  },
};

// سایز فونت‌ها بر اساس responsive design
export const fontSize = {
  xs: 10,
  sm: 12,
  base: 14,
  md: 16,
  lg: 18,
  xl: 20,
  '2xl': 24,
  '3xl': 28,
  '4xl': 32,
  '5xl': 36,
  '6xl': 48,
};

// ارتفاع خط برای متن‌های فارسی
export const lineHeight = {
  tight: 1.2,
  normal: 1.4,
  relaxed: 1.6,
  loose: 1.8,
};

// فاصله بین حروف
export const letterSpacing = {
  tighter: -0.5,
  tight: -0.25,
  normal: 0,
  wide: 0.25,
  wider: 0.5,
  widest: 1,
};

// تنظیمات فونت برای React Native
export const fontConfig = {
  default: {
    regular: {
      fontFamily: fontFamily.primary,
      fontWeight: 'normal',
    },
    medium: {
      fontFamily: fontFamily.vazir.medium,
      fontWeight: 'normal',
    },
    light: {
      fontFamily: fontFamily.vazir.light,
      fontWeight: 'normal',
    },
    thin: {
      fontFamily: fontFamily.vazir.thin,
      fontWeight: 'normal',
    },
  },
  ios: {
    regular: {
      fontFamily: fontFamily.primary,
      fontWeight: '400',
    },
    medium: {
      fontFamily: fontFamily.vazir.medium,
      fontWeight: '500',
    },
    light: {
      fontFamily: fontFamily.vazir.light,
      fontWeight: '300',
    },
    thin: {
      fontFamily: fontFamily.vazir.thin,
      fontWeight: '100',
    },
  },
  android: {
    regular: {
      fontFamily: fontFamily.primary,
      fontWeight: 'normal',
    },
    medium: {
      fontFamily: fontFamily.vazir.medium,
      fontWeight: 'normal',
    },
    light: {
      fontFamily: fontFamily.vazir.light,
      fontWeight: 'normal',
    },
    thin: {
      fontFamily: fontFamily.vazir.thin,
      fontWeight: 'normal',
    },
  },
  web: {
    regular: {
      fontFamily: fontFamily.primary,
      fontWeight: '400',
    },
    medium: {
      fontFamily: fontFamily.vazir.medium,
      fontWeight: '500',
    },
    light: {
      fontFamily: fontFamily.vazir.light,
      fontWeight: '300',
    },
    thin: {
      fontFamily: fontFamily.vazir.thin,
      fontWeight: '100',
    },
  },
};

// استایل‌های متن از پیش تعریف شده
export const textStyles = {
  // تیترها
  h1: {
    fontFamily: fontFamily.dana.bold,
    fontSize: fontSize['4xl'],
    lineHeight: lineHeight.tight,
    letterSpacing: letterSpacing.tight,
  },
  h2: {
    fontFamily: fontFamily.dana.bold,
    fontSize: fontSize['3xl'],
    lineHeight: lineHeight.tight,
    letterSpacing: letterSpacing.tight,
  },
  h3: {
    fontFamily: fontFamily.dana.demiBold,
    fontSize: fontSize['2xl'],
    lineHeight: lineHeight.normal,
    letterSpacing: letterSpacing.normal,
  },
  h4: {
    fontFamily: fontFamily.dana.medium,
    fontSize: fontSize.xl,
    lineHeight: lineHeight.normal,
    letterSpacing: letterSpacing.normal,
  },
  
  // متن‌های معمولی
  body1: {
    fontFamily: fontFamily.vazir.regular,
    fontSize: fontSize.md,
    lineHeight: lineHeight.relaxed,
    letterSpacing: letterSpacing.normal,
  },
  body2: {
    fontFamily: fontFamily.vazir.regular,
    fontSize: fontSize.base,
    lineHeight: lineHeight.relaxed,
    letterSpacing: letterSpacing.normal,
  },
  
  // متن‌های کوچک
  caption: {
    fontFamily: fontFamily.vazir.light,
    fontSize: fontSize.sm,
    lineHeight: lineHeight.normal,
    letterSpacing: letterSpacing.wide,
  },
  overline: {
    fontFamily: fontFamily.dana.medium,
    fontSize: fontSize.xs,
    lineHeight: lineHeight.normal,
    letterSpacing: letterSpacing.widest,
    textTransform: 'uppercase',
  },
  
  // دکمه‌ها
  button: {
    fontFamily: fontFamily.dana.demiBold,
    fontSize: fontSize.base,
    lineHeight: lineHeight.tight,
    letterSpacing: letterSpacing.wide,
  },
  
  // لیبل‌ها
  label: {
    fontFamily: fontFamily.vazir.medium,
    fontSize: fontSize.base,
    lineHeight: lineHeight.normal,
    letterSpacing: letterSpacing.normal,
  },
};

export default {
  fontFamily,
  fontSize,
  lineHeight,
  letterSpacing,
  fontConfig,
  textStyles,
};
