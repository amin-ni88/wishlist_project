import { MD3LightTheme as DefaultTheme } from 'react-native-paper';
import { I18nManager } from 'react-native';

export const theme = {
  ...DefaultTheme,
  isRTL: true,
  writingDirection: 'rtl' as const,
  colors: {
    ...DefaultTheme.colors,
    primary: '#17A6A3',    // Turquoise
    secondary: '#A7D7C5',  // Light mint green
    white: '#FFFFFF',
    black: '#000000',
    accent: '#136973',     // Dark teal
    background: '#F5F5F5',
    surface: '#FFFFFF',
    error: '#B00020',
    text: '#082D45',       // Dark navy
    onSurface: '#043E50',  // Petroleum blue
    disabled: '#BDBDBD',
    placeholder: '#9e9e9e',
    backdrop: 'rgba(8, 45, 69, 0.5)', // Navy with opacity
    notification: '#17A6A3',
  },
  roundness: 8,
  animation: {
    scale: 1.0,
  },
  typography: {
    h1: {
      fontSize: 32,
      fontWeight: 'bold',
    },
    h2: {
      fontSize: 24,
      fontWeight: 'bold',
    },
    h3: {
      fontSize: 20,
      fontWeight: 'bold',
    },
    body: {
      fontSize: 16,
    },
    small: {
      fontSize: 14,
    },
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },
};
