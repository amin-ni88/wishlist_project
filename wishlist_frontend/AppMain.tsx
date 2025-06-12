import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import HomePage from './HomePage';
import App from './App';

// Simple Component that uses HomePage
export default function AppMain() {
  const [currentScreen, setCurrentScreen] = useState('home'); // 'home' or 'login'

  const navigateToLogin = () => {
    setCurrentScreen('login');
  };

  const navigateToHome = () => {
    setCurrentScreen('home');
  };

  // Show HomePage
  if (currentScreen === 'home') {
    return <HomePage onNavigateToLogin={navigateToLogin} />;
  }

  // Show Login/Dashboard Page with back navigation
  return (
    <View style={styles.container}>
      {/* Back Button */}
      <View style={styles.backButtonContainer}>
        <TouchableOpacity style={styles.backButton} onPress={navigateToHome}>
          <Text style={styles.backButtonText}>← بازگشت به خانه</Text>
        </TouchableOpacity>
      </View>
      
      {/* Login App Component */}
      <App />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
  },
  backButtonContainer: {
    position: 'absolute',
    top: 50,
    left: 20,
    zIndex: 1000,
  },
  backButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
  },
  backButtonText: {
    color: '#17A6A3',
    fontSize: 14,
    fontWeight: '600',
  },
}); 