import React from 'react';
import { View, StyleSheet } from 'react-native';
import { ActivityIndicator, Text, Surface } from 'react-native-paper';

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
        <ActivityIndicator size="small" color="#17A6A3" />
        <Text style={styles.inlineText}>{message}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Surface style={styles.loadingCard}>
        <View style={styles.content}>
          <ActivityIndicator 
            size="large" 
            color="#17A6A3"
            style={styles.spinner}
          />
          <Text style={styles.message}>{message}</Text>
        </View>
      </Surface>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FAFAFA',
  },
  loadingCard: {
    borderRadius: 16,
    elevation: 8,
    padding: 32,
    backgroundColor: '#FFFFFF',
  },
  content: {
    alignItems: 'center',
  },
  spinner: {
    marginBottom: 16,
  },
  message: {
    fontSize: 16,
    color: '#043E50',
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
    color: '#043E50',
  },
});

export default LoadingScreen; 