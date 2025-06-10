import { StatusBar } from 'expo-status-bar';
import React from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Provider as PaperProvider } from 'react-native-paper';
import { I18nManager } from 'react-native';
import { theme } from './src/utils/theme';
import { AuthProvider, useAuth } from './src/context/AuthContext';
import { RightToLeftProvider } from './src/context/RightToLeftContext';
import AppNavigator from './src/navigation/AppNavigator';
import LoadingScreen from './src/components/common/LoadingScreen';

// Force RTL layout
I18nManager.allowRTL(true);
I18nManager.forceRTL(true);

const AppContent = () => {
  const { isLoading } = useAuth();

  if (isLoading) {
    return <LoadingScreen message="در حال بارگذاری اپلیکیشن..." />;
  }

  return <AppNavigator />;
};

export default function App() {
  return (
    <SafeAreaProvider>
      <PaperProvider theme={theme}>
        <RightToLeftProvider>
          <AuthProvider>
            <AppContent />
            <StatusBar style="auto" />
          </AuthProvider>
        </RightToLeftProvider>
      </PaperProvider>
    </SafeAreaProvider>
  );
}
