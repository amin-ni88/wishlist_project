import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import {
  TextInput,
  Button,
  Title,
  Card,
  Text,
  ActivityIndicator,
} from 'react-native-paper';
import { useAuth } from '../../context/AuthContext';
import { authAPI } from '../../services/api';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface LoginScreenProps {
  navigation: any;
}

const LoginScreen: React.FC<LoginScreenProps> = ({ navigation }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      Alert.alert('خطا', 'لطفا نام کاربری و رمز عبور را وارد کنید');
      return;
    }

    setLoading(true);
    try {
      const response = await authAPI.login({ username, password });
      const { access, refresh, user } = response.data;

      await AsyncStorage.setItem('access_token', access);
      await AsyncStorage.setItem('refresh_token', refresh);
      await AsyncStorage.setItem('user', JSON.stringify(user));

      login(user, access);
      navigation.replace('Main');
    } catch (error: any) {
      console.error('Login error:', error);
      Alert.alert(
        'خطا در ورود',
        error.response?.data?.detail || 'نام کاربری یا رمز عبور اشتباه است'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <Card style={styles.card}>
          <Card.Content>
            <Title style={styles.title}>ورود به حساب کاربری</Title>
            
            <TextInput
              label="نام کاربری"
              value={username}
              onChangeText={setUsername}
              mode="outlined"
              style={styles.input}
              autoCapitalize="none"
              autoCorrect={false}
              disabled={loading}
            />

            <TextInput
              label="رمز عبور"
              value={password}
              onChangeText={setPassword}
              mode="outlined"
              secureTextEntry
              style={styles.input}
              disabled={loading}
            />

            <Button
              mode="contained"
              onPress={handleLogin}
              style={styles.button}
              disabled={loading}
            >
              {loading ? <ActivityIndicator color="white" /> : 'ورود'}
            </Button>

            <View style={styles.registerContainer}>
              <Text>حساب کاربری ندارید؟ </Text>
              <Button
                mode="text"
                onPress={() => navigation.navigate('Register')}
                disabled={loading}
              >
                ثبت نام
              </Button>
            </View>
          </Card.Content>
        </Card>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  card: {
    elevation: 4,
    borderRadius: 12,
  },
  title: {
    textAlign: 'center',
    marginBottom: 30,
    fontSize: 24,
    fontWeight: 'bold',
  },
  input: {
    marginBottom: 16,
  },
  button: {
    marginTop: 16,
    paddingVertical: 8,
  },
  registerContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 20,
  },
});

export default LoginScreen;
