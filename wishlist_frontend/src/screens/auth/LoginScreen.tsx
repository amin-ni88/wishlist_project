import React, { useState } from 'react';
import { StyleSheet, View } from 'react-native';
import { TextInput, Button, Text } from 'react-native-paper';
import { theme } from '../../utils/theme';

const LoginScreen = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = () => {
    // Handle login logic
  };

  return (
    <View style={styles.container}>
      <View style={styles.logoContainer}>
        <Text style={styles.title}>آرزوها</Text>
        <Text style={styles.subtitle}>لیست آرزوهای خود را مدیریت کنید</Text>
      </View>

      <View style={styles.formContainer}>
        <TextInput
          label="ایمیل"
          value={email}
          onChangeText={setEmail}
          style={styles.input}
          keyboardType="email-address"
          autoCapitalize="none"
        />

        <TextInput
          label="رمز عبور"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          style={styles.input}
        />

        <Button
          mode="contained"
          onPress={handleLogin}
          style={styles.loginButton}
          contentStyle={styles.loginButtonContent}
        >
          ورود
        </Button>

        <Button
          mode="text"
          onPress={() => navigation.navigate('Register')}
          style={styles.registerButton}
        >
          ثبت‌نام
        </Button>
      </View>
    </View>
  );
};

import { useRTL, createRTLStyles } from '../../context/RightToLeftContext';

const styles = createRTLStyles({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
    padding: theme.spacing.lg,
  },
  logoContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    ...theme.typography.h1,
    color: theme.colors.primary,
    marginBottom: theme.spacing.sm,
  },
  subtitle: {
    ...theme.typography.body,
    color: theme.colors.onSurface,
  },
  formContainer: {
    flex: 2,
    justifyContent: 'center',
  },
  input: {
    marginBottom: theme.spacing.md,
    backgroundColor: theme.colors.surface,
  },
  loginButton: {
    marginTop: theme.spacing.md,
    backgroundColor: theme.colors.accent,
  },
  loginButtonContent: {
    padding: theme.spacing.sm,
  },
  registerButton: {
    marginTop: theme.spacing.md,
  },
});

export default LoginScreen;
