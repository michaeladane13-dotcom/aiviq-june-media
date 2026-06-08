import React from 'react';
import { SafeAreaView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import palette from '../../constants/palette';

export default function Welcome({ navigation }) {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.logoCircle}>
          <Text style={styles.logoText}>C</Text>
        </View>

        <Text style={styles.title}>Welcome to Chaya</Text>
        <Text style={styles.subtitle}>Your daily spiritual guide</Text>
      </View>

      <TouchableOpacity style={styles.button} onPress={() => navigation.navigate('Name')}>
        <Text style={styles.buttonText}>Begin</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: palette.background,
    paddingHorizontal: 24,
    paddingTop: 24,
    paddingBottom: 32,
    justifyContent: 'space-between',
  },
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoCircle: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: palette.surfaceAlt,
    borderWidth: 2,
    borderColor: palette.gold,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 32,
    shadowColor: palette.gold,
    shadowOpacity: 0.2,
    shadowRadius: 20,
    shadowOffset: { width: 0, height: 8 },
  },
  logoText: {
    color: palette.gold,
    fontSize: 56,
    fontWeight: '700',
  },
  title: {
    color: palette.text,
    fontSize: 32,
    fontWeight: '700',
    textAlign: 'center',
    marginBottom: 12,
  },
  subtitle: {
    color: palette.muted,
    fontSize: 17,
    textAlign: 'center',
  },
  button: {
    backgroundColor: palette.gold,
    borderRadius: 16,
    paddingVertical: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    color: palette.background,
    fontSize: 17,
    fontWeight: '700',
  },
});
