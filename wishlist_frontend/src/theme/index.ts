export const colors = {
  // Primary Colors
  primary: '#6C5CE7',
  secondary: '#A29BFE',
  
  // Accent Colors
  turquoise: '#00CEC9',
  emerald: '#00B894',
  
  // Status Colors
  success: '#00B894',
  warning: '#FDCB6E',
  error: '#E84393',
  info: '#74B9FF',
  
  // Neutral Colors
  background: '#F8F9FA',
  surface: '#FFFFFF',
  border: '#E2E8F0',
  
  // Text Colors
  textPrimary: '#2D3436',
  textSecondary: '#636E72',
  textTertiary: '#B2BEC3',
  textDisabled: '#DDD6FE',
  
  // Additional Colors
  white: '#FFFFFF',
  black: '#000000',
  disabled: '#B2BEC3',
  
  // Gradient Colors
  gradientStart: '#6C5CE7',
  gradientEnd: '#A29BFE',
};

export const typography = {
  // Headers
  h1: {
    fontSize: 32,
    fontWeight: '700' as const,
    lineHeight: 40,
    fontFamily: 'Dana-Bold',
  },
  h2: {
    fontSize: 28,
    fontWeight: '600' as const,
    lineHeight: 36,
    fontFamily: 'Dana-SemiBold',
  },
  h3: {
    fontSize: 24,
    fontWeight: '600' as const,
    lineHeight: 32,
    fontFamily: 'Dana-SemiBold',
  },
  h4: {
    fontSize: 20,
    fontWeight: '500' as const,
    lineHeight: 28,
    fontFamily: 'Dana-Medium',
  },
  h5: {
    fontSize: 18,
    fontWeight: '500' as const,
    lineHeight: 24,
    fontFamily: 'Dana-Medium',
  },
  h6: {
    fontSize: 16,
    fontWeight: '500' as const,
    lineHeight: 22,
    fontFamily: 'Dana-Medium',
  },
  
  // Body Text
  body: {
    fontSize: 16,
    fontWeight: '400' as const,
    lineHeight: 24,
    fontFamily: 'Vazir-Regular',
  },
  bodySmall: {
    fontSize: 14,
    fontWeight: '400' as const,
    lineHeight: 20,
    fontFamily: 'Vazir-Regular',
  },
  
  // UI Elements
  button: {
    fontSize: 16,
    fontWeight: '600' as const,
    lineHeight: 20,
    fontFamily: 'Dana-SemiBold',
  },
  caption: {
    fontSize: 12,
    fontWeight: '400' as const,
    lineHeight: 16,
    fontFamily: 'Vazir-Regular',
  },
  overline: {
    fontSize: 10,
    fontWeight: '500' as const,
    lineHeight: 12,
    letterSpacing: 1.5,
    textTransform: 'uppercase' as const,
    fontFamily: 'Vazir-Medium',
  },
  
  // Input
  input: {
    fontSize: 16,
    fontWeight: '400' as const,
    lineHeight: 24,
    fontFamily: 'Vazir-Regular',
  },
  
  // Navigation
  navTitle: {
    fontSize: 18,
    fontWeight: '600' as const,
    lineHeight: 24,
    fontFamily: 'Dana-SemiBold',
  },
  navLabel: {
    fontSize: 12,
    fontWeight: '500' as const,
    lineHeight: 16,
    fontFamily: 'Vazir-Medium',
  },
};

export const spacing = {
  // Base spacing
  xs: 4,
  small: 8,
  medium: 16,
  large: 24,
  xl: 32,
  xxl: 48,
  
  // Specific spacing
  screenPadding: 16,
  cardPadding: 16,
  cardMargin: 8,
  buttonHeight: 48,
  inputHeight: 48,
  tabBarHeight: 60,
  headerHeight: 56,
  
  // Border radius
  borderRadiusSmall: 4,
  borderRadiusMedium: 8,
  borderRadiusLarge: 12,
  borderRadiusXL: 16,
  borderRadiusRound: 50,
};

export const shadows = {
  small: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  medium: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 4,
  },
  large: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 8,
  },
};

export const animations = {
  // Duration
  durationFast: 200,
  durationNormal: 300,
  durationSlow: 500,
  
  // Easing
  easeInOut: 'ease-in-out',
  easeIn: 'ease-in',
  easeOut: 'ease-out',
};

// Responsive breakpoints
export const breakpoints = {
  mobile: 480,
  tablet: 768,
  desktop: 1024,
};

// Theme object combining all design tokens
export const theme = {
  colors,
  typography,
  spacing,
  shadows,
  animations,
  breakpoints,
};

export default theme; 