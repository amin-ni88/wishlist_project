import React from 'react';
import { View, StyleSheet } from 'react-native';
import { ActivityIndicator, Text, Surface } from 'react-native-paper';
import { LinearGradient } from 'expo-linear-gradient';
import { theme } from '../../utils/theme';

interface LoadingScreenProps {
  message?: string;
  fullScreen?: boolean;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({ 
  message = 'در حال بارگذاری...', 
  fullScreen = true 
}) => {
  if (!fullScreen) {
    return (
      <View style={styles.inlineContainer}>
        <ActivityIndicator size="small" color={theme.colors.primary} />
        <Text style={styles.inlineText}>{message}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={[theme.colors.primary, theme.colors.accent]}
        style={styles.gradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <Surface style={styles.loadingCard}>
          <View style={styles.content}>
            <ActivityIndicator 
              size="large" 
              color={theme.colors.primary}
              style={styles.spinner}
            />
            <Text style={styles.message}>{message}</Text>
          </View>
        </Surface>
      </LinearGradient>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  gradient: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingCard: {
    borderRadius: 16,
    elevation: 8,
    padding: 32,
    backgroundColor: theme.colors.surface,
  },
  content: {
    alignItems: 'center',
  },
  spinner: {
    marginBottom: 16,
  },
  message: {
    fontSize: 16,
    color: theme.colors.text,
    textAlign: 'center',
  },
  inlineContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
  },
  inlineText: {
    marginLeft: 12,
    color: theme.colors.text,
  },
});

export default LoadingScreen; 