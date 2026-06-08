import React, { useMemo, useState } from 'react';
import {
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import palette from '../../constants/palette';

export default function Name({ navigation }) {
  const [firstName, setFirstName] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const nameError = useMemo(() => {
    if (!submitted) {
      return '';
    }

    if (!firstName.trim()) {
      return 'Please enter your first name.';
    }

    return '';
  }, [firstName, submitted]);

  const handleNext = () => {
    setSubmitted(true);

    if (!firstName.trim()) {
      return;
    }

    navigation.navigate('BirthData', {
      firstName: firstName.trim(),
    });
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.keyboard}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <View>
          <Text style={styles.title}>What shall I call you?</Text>
          <Text style={styles.subtitle}>
            Enter the name you want Chaya to use in your daily guidance.
          </Text>

          <View style={styles.fieldGroup}>
            <Text style={styles.label}>First name</Text>
            <TextInput
              style={[styles.input, nameError ? styles.inputError : null]}
              placeholder="Your first name"
              placeholderTextColor={palette.muted}
              value={firstName}
              onChangeText={setFirstName}
              autoCapitalize="words"
              returnKeyType="done"
            />
            {nameError ? <Text style={styles.errorText}>{nameError}</Text> : null}
          </View>
        </View>

        <TouchableOpacity style={styles.button} onPress={handleNext}>
          <Text style={styles.buttonText}>Next</Text>
        </TouchableOpacity>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: palette.background,
  },
  keyboard: {
    flex: 1,
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingTop: 48,
    paddingBottom: 32,
  },
  title: {
    color: palette.text,
    fontSize: 30,
    fontWeight: '700',
    marginBottom: 12,
  },
  subtitle: {
    color: palette.muted,
    fontSize: 16,
    lineHeight: 24,
    marginBottom: 28,
  },
  fieldGroup: {
    marginTop: 8,
  },
  label: {
    color: palette.goldSoft,
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 10,
  },
  input: {
    backgroundColor: palette.surface,
    borderColor: palette.border,
    borderWidth: 1,
    borderRadius: 16,
    paddingHorizontal: 16,
    paddingVertical: 16,
    color: palette.text,
    fontSize: 16,
  },
  inputError: {
    borderColor: palette.error,
  },
  errorText: {
    color: palette.error,
    fontSize: 13,
    marginTop: 8,
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
