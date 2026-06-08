import React from 'react';
import { NavigationContainer, DarkTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Ionicons from 'react-native-vector-icons/Ionicons';
import Welcome from '../screens/onboarding/Welcome';
import Name from '../screens/onboarding/Name';
import BirthData from '../screens/onboarding/BirthData';
import Account from '../screens/onboarding/Account';
import Home from '../screens/Home';
import Paywall from '../screens/Paywall';
import palette from '../constants/palette';

const OnboardingStack = createNativeStackNavigator();
const MainStack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const navigationTheme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    primary: palette.gold,
    background: palette.background,
    card: palette.surface,
    text: palette.text,
    border: palette.border,
    notification: palette.purpleBright,
  },
};

function OnboardingNavigator() {
  return (
    <OnboardingStack.Navigator
      initialRouteName="Welcome"
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: palette.background },
        animation: 'slide_from_right',
      }}
    >
      <OnboardingStack.Screen name="Welcome" component={Welcome} />
      <OnboardingStack.Screen name="Name" component={Name} />
      <OnboardingStack.Screen name="BirthData" component={BirthData} />
      <OnboardingStack.Screen name="Account" component={Account} />
    </OnboardingStack.Navigator>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: palette.surface,
          borderTopColor: palette.border,
          height: 70,
          paddingTop: 8,
          paddingBottom: 10,
        },
        tabBarActiveTintColor: palette.gold,
        tabBarInactiveTintColor: palette.muted,
      }}
    >
      <Tab.Screen
        name="HomeTab"
        component={Home}
        options={{
          title: 'Home',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="sparkles-outline" size={size} color={color} />
          ),
        }}
      />
    </Tab.Navigator>
  );
}

function MainNavigator() {
  return (
    <MainStack.Navigator
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: palette.background },
        animation: 'slide_from_right',
      }}
    >
      <MainStack.Screen name="MainTabs" component={MainTabs} />
      <MainStack.Screen name="Paywall" component={Paywall} />
    </MainStack.Navigator>
  );
}

export default function RootNavigator({ session }) {
  return (
    <NavigationContainer theme={navigationTheme}>
      {session ? <MainNavigator /> : <OnboardingNavigator />}
    </NavigationContainer>
  );
}
