import React from 'react';
import { View, StyleSheet, Dimensions } from 'react-native';

const { width, height } = Dimensions.get('window');

interface ResponsiveLayoutProps {
  children: React.ReactNode;
  mobileComponent?: React.ReactNode;
  tabletComponent?: React.ReactNode;
  desktopComponent?: React.ReactNode;
}

export const getDeviceType = () => {
  if (width >= 1200) return 'desktop';
  if (width >= 768) return 'tablet';
  return 'mobile';
};

export const isTablet = width >= 768 && width < 1200;
export const isDesktop = width >= 1200;
export const isMobile = width < 768;

const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({
  children,
  mobileComponent,
  tabletComponent,
  desktopComponent,
}) => {
  const deviceType = getDeviceType();

  // Return specific component based on device type
  if (deviceType === 'desktop' && desktopComponent) {
    return <View style={styles.container}>{desktopComponent}</View>;
  }
  
  if (deviceType === 'tablet' && tabletComponent) {
    return <View style={styles.container}>{tabletComponent}</View>;
  }
  
  if (deviceType === 'mobile' && mobileComponent) {
    return <View style={styles.container}>{mobileComponent}</View>;
  }

  // Default: return children with responsive container
  return (
    <View style={[
      styles.container,
      deviceType === 'desktop' && styles.desktopContainer,
      deviceType === 'tablet' && styles.tabletContainer,
    ]}>
      {children}
    </View>
  );
};

export const ResponsiveGrid: React.FC<{
  children: React.ReactNode;
  minItemWidth?: number;
}> = ({ children, minItemWidth = 300 }) => {
  const columns = Math.floor(width / minItemWidth) || 1;
  
  return (
    <View style={[styles.grid, { gap: 16 }]}>
      {children}
    </View>
  );
};

export const ResponsivePadding = {
  horizontal: isMobile ? 16 : isTablet ? 32 : 48,
  vertical: isMobile ? 16 : isTablet ? 24 : 32,
};

export const ResponsiveFontSize = {
  h1: isMobile ? 24 : isTablet ? 28 : 32,
  h2: isMobile ? 20 : isTablet ? 22 : 24,
  h3: isMobile ? 18 : isTablet ? 20 : 22,
  body: isMobile ? 14 : isTablet ? 15 : 16,
  small: isMobile ? 12 : isTablet ? 13 : 14,
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  desktopContainer: {
    maxWidth: 1200,
    alignSelf: 'center',
    paddingHorizontal: 48,
  },
  tabletContainer: {
    paddingHorizontal: 32,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
});

export default ResponsiveLayout; 