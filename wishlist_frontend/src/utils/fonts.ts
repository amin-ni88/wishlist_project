// Simplified Fonts Configuration for Web Compatibility
export const fontFamily = {
  primary: 'system-ui, -apple-system, sans-serif',
  secondary: 'system-ui, -apple-system, sans-serif', 
  english: 'system-ui, -apple-system, sans-serif',
  
  vazir: {
    thin: 'system-ui, -apple-system, sans-serif',
    light: 'system-ui, -apple-system, sans-serif',
    regular: 'system-ui, -apple-system, sans-serif',
    medium: 'system-ui, -apple-system, sans-serif',
    bold: 'system-ui, -apple-system, sans-serif',
    black: 'system-ui, -apple-system, sans-serif',
  },
  
  dana: {
    thin: 'system-ui, -apple-system, sans-serif',
    light: 'system-ui, -apple-system, sans-serif',
    regular: 'system-ui, -apple-system, sans-serif',
    medium: 'system-ui, -apple-system, sans-serif',
    demiBold: 'system-ui, -apple-system, sans-serif',
    bold: 'system-ui, -apple-system, sans-serif',
    extraBold: 'system-ui, -apple-system, sans-serif',
    black: 'system-ui, -apple-system, sans-serif',
  },
};

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

export const lineHeight = {
  tight: 1.2,
  normal: 1.4,
  relaxed: 1.6,
  loose: 1.8,
};

export const letterSpacing = {
  tighter: -0.5,
  tight: -0.25,
  normal: 0,
  wide: 0.25,
  wider: 0.5,
  widest: 1,
};

export const fontConfig = {
  default: {
    regular: {
      fontFamily: fontFamily.primary,
      fontWeight: '400',
    },
    medium: {
      fontFamily: fontFamily.primary,
      fontWeight: '500',
    },
    light: {
      fontFamily: fontFamily.primary,
      fontWeight: '300',
    },
    thin: {
      fontFamily: fontFamily.primary,
      fontWeight: '100',
    },
  },
};

export const textStyles = {
  h1: {
    fontFamily: fontFamily.primary,
    fontSize: fontSize['4xl'],
    fontWeight: '700',
    lineHeight: lineHeight.tight,
  },
  h2: {
    fontFamily: fontFamily.primary,
    fontSize: fontSize['3xl'],
    fontWeight: '700',
    lineHeight: lineHeight.tight,
  },
  h3: {
    fontFamily: fontFamily.primary,
    fontSize: fontSize['2xl'],
    fontWeight: '600',
    lineHeight: lineHeight.normal,
  },
  h4: {
    fontFamily: fontFamily.primary,
    fontSize: fontSize.xl,
    fontWeight: '500',
    lineHeight: lineHeight.normal,
  },
  body1: {
    fontFamily: fontFamily.primary,
    fontSize: fontSize.md,
    fontWeight: '400',
    lineHeight: lineHeight.relaxed,
  },
  body2: {
    fontFamily: fontFamily.primary,
    fontSize: fontSize.base,
    fontWeight: '400',
    lineHeight: lineHeight.relaxed,
  },
  caption: {
    fontFamily: fontFamily.primary,
    fontSize: fontSize.sm,
    fontWeight: '300',
    lineHeight: lineHeight.normal,
  },
  button: {
    fontFamily: fontFamily.primary,
    fontSize: fontSize.base,
    fontWeight: '600',
    lineHeight: lineHeight.tight,
  },
  label: {
    fontFamily: fontFamily.primary,
    fontSize: fontSize.base,
    fontWeight: '500',
    lineHeight: lineHeight.normal,
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
