import React, { useState } from 'react';
import { StyleSheet, View, ScrollView } from 'react-native';
import { TextInput, Button, Text } from 'react-native-paper';
import { theme } from '../../utils/theme';

const RegisterScreen = ({ navigation }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleRegister = () => {
    // Handle registration logic
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.headerContainer}>
        <Text style={styles.title}>ثبت‌نام</Text>
        <Text style={styles.subtitle}>به جمع ما بپیوندید</Text>
      </View>

      <View style={styles.formContainer}>
        <TextInput
          label="نام"
          value={name}
          onChangeText={setName}
          style={styles.input}
        />

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

        <TextInput
          label="تکرار رمز عبور"
          value={confirmPassword}
          onChangeText={setConfirmPassword}
          secureTextEntry
          style={styles.input}
        />

        <Button
          mode="contained"
          onPress={handleRegister}
          style={styles.registerButton}
          contentStyle={styles.registerButtonContent}
        >
          ثبت‌نام
        </Button>

        <Button
          mode="text"
          onPress={() => navigation.navigate('Login')}
          style={styles.loginButton}
        >
          بازگشت به صفحه ورود
        </Button>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    padding: theme.spacing.lg,
    minHeight: '100%',
  },
  headerContainer: {
    marginTop: theme.spacing.xl * 2,
    marginBottom: theme.spacing.xl,
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
    flex: 1,
    justifyContent: 'center',
  },
  input: {
    marginBottom: theme.spacing.md,
    backgroundColor: theme.colors.surface,
  },
  registerButton: {
    marginTop: theme.spacing.lg,
    backgroundColor: theme.colors.accent,
  },
  registerButtonContent: {
    padding: theme.spacing.sm,
  },
  loginButton: {
    marginTop: theme.spacing.md,
  },
});

export default RegisterScreen;
