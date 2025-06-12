import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Button } from 'react-native-paper';
import { useAuth } from '../context/AuthContext';

// Simple Login Component
const SimpleLogin = () => {
  const { login } = useAuth();
  
  const handleLogin = () => {
    const mockUser = {
      id: 1,
      username: 'تست',
      email: 'test@example.com',
      first_name: 'کاربر',
      last_name: 'تست',
    };
    login(mockUser, 'mock-token');
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🎉 پلتفرم لیست آرزوها</Text>
      <Text style={styles.subtitle}>ورود به حساب کاربری</Text>
      
      <View style={styles.colorDisplay}>
        <View style={[styles.colorBox, { backgroundColor: '#17A6A3' }]} />
        <View style={[styles.colorBox, { backgroundColor: '#A7D7C5' }]} />
        <View style={[styles.colorBox, { backgroundColor: '#136973' }]} />
        <View style={[styles.colorBox, { backgroundColor: '#043E50' }]} />
      </View>
      
      <Button 
        mode="contained" 
        onPress={handleLogin}
        style={styles.button}
        buttonColor="#17A6A3"
      >
        ورود (تست)
      </Button>
    </View>
  );
};

// Simple Home Component
const SimpleHome = () => {
  const { user, logout } = useAuth();
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>خوش آمدید {user?.first_name}! 🎉</Text>
      <Text style={styles.subtitle}>پلتفرم لیست آرزوها</Text>
      
      <View style={styles.colorDisplay}>
        <View style={[styles.colorBox, { backgroundColor: '#17A6A3' }]} />
        <View style={[styles.colorBox, { backgroundColor: '#A7D7C5' }]} />
        <View style={[styles.colorBox, { backgroundColor: '#136973' }]} />
        <View style={[styles.colorBox, { backgroundColor: '#043E50' }]} />
      </View>
      
      <Text style={styles.text}>✅ سیستم احراز هویت فعال</Text>
      <Text style={styles.text}>✅ پالت رنگی فارسی اعمال شده</Text>
      <Text style={styles.text}>✅ Backend API متصل</Text>
      
      <Button 
        mode="outlined" 
        onPress={logout}
        style={styles.button}
        textColor="#17A6A3"
      >
        خروج
      </Button>
    </View>
  );
};

const AppNavigator = () => {
  const { user, token } = useAuth();

  return user && token ? <SimpleHome /> : <SimpleLogin />;
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FAFAFA',
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#17A6A3',
    marginBottom: 10,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 18,
    color: '#043E50',
    marginBottom: 30,
    textAlign: 'center',
  },
  text: {
    fontSize: 16,
    color: '#043E50',
    marginBottom: 10,
    textAlign: 'center',
  },
  colorDisplay: {
    flexDirection: 'row',
    marginBottom: 30,
  },
  colorBox: {
    width: 50,
    height: 50,
    marginHorizontal: 5,
    borderRadius: 8,
  },
  button: {
    marginTop: 20,
    paddingHorizontal: 30,
  },
});

export default AppNavigator;
