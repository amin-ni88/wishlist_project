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
import { authAPI } from '../../services/api';

interface RegisterScreenProps {
  navigation: any;
}

const RegisterScreen: React.FC<RegisterScreenProps> = ({ navigation }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
  });
  const [loading, setLoading] = useState(false);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const validateForm = () => {
    if (!formData.username.trim()) {
      Alert.alert('خطا', 'نام کاربری الزامی است');
      return false;
    }
    if (!formData.email.trim()) {
      Alert.alert('خطا', 'ایمیل الزامی است');
      return false;
    }
    if (!formData.password.trim()) {
      Alert.alert('خطا', 'رمز عبور الزامی است');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      Alert.alert('خطا', 'رمز عبور و تکرار آن یکسان نیستند');
      return false;
    }
    if (formData.password.length < 6) {
      Alert.alert('خطا', 'رمز عبور باید حداقل ۶ کاراکتر باشد');
      return false;
    }
    return true;
  };

  const handleRegister = async () => {
    if (!validateForm()) return;

    setLoading(true);
    try {
      const { confirmPassword, ...registerData } = formData;
      await authAPI.register(registerData);
      
      Alert.alert(
        'موفقیت',
        'حساب کاربری شما با موفقیت ایجاد شد. اکنون می‌توانید وارد شوید.',
        [{ text: 'باشه', onPress: () => navigation.navigate('Login') }]
      );
    } catch (error: any) {
      console.error('Register error:', error);
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.username?.[0] ||
                          error.response?.data?.email?.[0] ||
                          'خطا در ثبت نام';
      Alert.alert('خطا در ثبت نام', errorMessage);
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
            <Title style={styles.title}>ثبت نام</Title>
            
            <TextInput
              label="نام کاربری"
              value={formData.username}
              onChangeText={(value) => handleInputChange('username', value)}
              mode="outlined"
              style={styles.input}
              autoCapitalize="none"
              autoCorrect={false}
              disabled={loading}
            />

            <TextInput
              label="ایمیل"
              value={formData.email}
              onChangeText={(value) => handleInputChange('email', value)}
              mode="outlined"
              style={styles.input}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
              disabled={loading}
            />

            <View style={styles.nameContainer}>
              <TextInput
                label="نام"
                value={formData.first_name}
                onChangeText={(value) => handleInputChange('first_name', value)}
                mode="outlined"
                style={[styles.input, styles.halfInput]}
                disabled={loading}
              />
              
              <TextInput
                label="نام خانوادگی"
                value={formData.last_name}
                onChangeText={(value) => handleInputChange('last_name', value)}
                mode="outlined"
                style={[styles.input, styles.halfInput]}
                disabled={loading}
              />
            </View>

            <TextInput
              label="رمز عبور"
              value={formData.password}
              onChangeText={(value) => handleInputChange('password', value)}
              mode="outlined"
              secureTextEntry
              style={styles.input}
              disabled={loading}
            />

            <TextInput
              label="تکرار رمز عبور"
              value={formData.confirmPassword}
              onChangeText={(value) => handleInputChange('confirmPassword', value)}
              mode="outlined"
              secureTextEntry
              style={styles.input}
              disabled={loading}
            />

            <Button
              mode="contained"
              onPress={handleRegister}
              style={styles.button}
              disabled={loading}
            >
              {loading ? <ActivityIndicator color="white" /> : 'ثبت نام'}
            </Button>

            <View style={styles.loginContainer}>
              <Text>قبلا ثبت نام کرده‌اید؟ </Text>
              <Button
                mode="text"
                onPress={() => navigation.navigate('Login')}
                disabled={loading}
              >
                ورود
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
  nameContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  halfInput: {
    width: '48%',
  },
  button: {
    marginTop: 16,
    paddingVertical: 8,
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 20,
  },
});

export default RegisterScreen;
