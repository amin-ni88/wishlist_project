import { StatusBar } from 'expo-status-bar';
import React from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Provider as PaperProvider } from 'react-native-paper';
import { I18nManager } from 'react-native';
import { theme } from './src/utils/theme';
import { AuthProvider } from './src/context/AuthContext';
import { RightToLeftProvider } from './src/context/RightToLeftContext';
import AppNavigator from './src/navigation/AppNavigator';

// Force RTL layout
I18nManager.allowRTL(true);
I18nManager.forceRTL(true);

export default function App() {
  return (
    <SafeAreaProvider>
      <PaperProvider theme={theme}>
        <RightToLeftProvider>
          <AuthProvider>
            <AppNavigator />
          </AuthProvider>
        </RightToLeftProvider>
      </PaperProvider>
    </SafeAreaProvider>
  );
}
