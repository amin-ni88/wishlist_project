import React from 'react';

export type RootStackParamList = {
  Login: undefined;
  Register: undefined;
  Main: undefined;
  WishlistDetail: { id: number };
  WishlistItemDetail: { id: number };
  AddWishlistItem: { wishlistId: number };
  EditWishlistItem: { id: number };
  Payment: { itemId: number; amount: number };
  ShareWishlist: { wishlistId: number };
  Invitation: { token: string };
};
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { theme } from '../utils/theme';

// Auth Screens
import LoginScreen from '../screens/auth/LoginScreen';
import RegisterScreen from '../screens/auth/RegisterScreen';

// Main Screens
import { HomeScreen } from '../screens/HomeScreen';
import { AddWishlistItemScreen } from '../screens/AddWishlistItemScreen';
import { WishlistItemDetailScreen } from '../screens/WishlistItemDetailScreen';
import { CreateWishlistScreen } from '../screens/CreateWishlistScreen';

// Profile Screens
import ProfileScreen from '../screens/profile/ProfileScreen';
// import WalletScreen from '../screens/profile/WalletScreen';
// import SettingsScreen from '../screens/profile/SettingsScreen';

// Notification Screen
// import NotificationScreen from '../screens/notifications/NotificationScreen';

// Payment Screen
import PaymentScreen from '../screens/PaymentScreen';

// Share Screen
import ShareWishlistScreen from '../screens/ShareWishlistScreen';
import InvitationScreen from '../screens/InvitationScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const AuthNavigator = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
    </Stack.Navigator>
  );
};

const MainTabNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: true,
        tabBarStyle: {
          backgroundColor: theme.colors.surface,
          borderTopWidth: 1,
          borderTopColor: '#e0e0e0',
          height: 60,
          paddingBottom: 8,
          paddingTop: 8,
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.disabled,
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'AddItem') {
            iconName = focused ? 'add-circle' : 'add-circle-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          } else if (route.name === 'Notifications') {
            iconName = focused ? 'notifications' : 'notifications-outline';
          } else {
            iconName = 'help-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{
          title: 'آرزوهای من',
          tabBarLabel: 'خانه',
        }}
      />
      <Tab.Screen 
        name="AddItem" 
        component={AddWishlistItemScreen}
        options={{
          title: 'افزودن آیتم',
          tabBarLabel: 'افزودن',
        }}
      />
      {/* <Tab.Screen 
        name="Notifications" 
        component={NotificationScreen}
        options={{
          title: 'اعلان‌ها',
          tabBarLabel: 'اعلان‌ها',
        }}
      /> */}
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          title: 'پروفایل',
          tabBarLabel: 'پروفایل',
        }}
      />
    </Tab.Navigator>
  );
};

const MainNavigator = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: theme.colors.primary,
        },
        headerTintColor: theme.colors.white,
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Stack.Screen 
        name="MainTabs" 
        component={MainTabNavigator}
        options={{ headerShown: false }}
      />
      <Stack.Screen 
        name="ItemDetail" 
        component={WishlistItemDetailScreen}
        options={{ title: 'جزئیات آیتم' }}
      />
      <Stack.Screen 
        name="CreateWishlist" 
        component={CreateWishlistScreen}
        options={{ title: 'ایجاد لیست آرزو' }}
      />
      {/* <Stack.Screen 
        name="Wallet" 
        component={WalletScreen}
        options={{ title: 'کیف پول' }}
      />
      <Stack.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{ title: 'تنظیمات' }}
      /> */}
      <Stack.Screen 
        name="Payment" 
        component={PaymentScreen}
        options={{ title: 'پرداخت' }}
      />
      <Stack.Screen 
        name="ShareWishlist" 
        component={ShareWishlistScreen}
        options={{ title: 'اشتراک‌گذاری' }}
      />
      <Stack.Screen 
        name="Invitation" 
        component={InvitationScreen}
        options={{ title: 'دعوت‌نامه' }}
      />
    </Stack.Navigator>
  );
};

const AppNavigator = () => {
  const { user, token } = useAuth();

  return (
    <NavigationContainer>
      {user && token ? <MainNavigator /> : <AuthNavigator />}
    </NavigationContainer>
  );
};

export default AppNavigator;
