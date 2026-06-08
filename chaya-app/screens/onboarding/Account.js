import React, { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
} from 'react-native';
import palette from '../../constants/palette';
import { supabase } from '../../lib/supabaseClient';

function isValidEmail(email) {
  return /\S+@\S+\.\S+/.test(email.trim());
}

export default function Account({ navigation, route }) {
  const { firstName, birthDate, birthTime, knowsBirthTime, city } = route.params;

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [inlineError, setInlineError] = useState('');
  const [needsConfirmation, setNeedsConfirmation] = useState(false);

  useEffect(() => {
    if (inlineError) {
      setInlineError('');
    }
  }, [email, password]);

  const emailError = useMemo(() => {
    if (!submitted) {
      return '';
    }

    if (!email.trim()) {
      return 'Email is required.';
    }

    if (!isValidEmail(email)) {
      return 'Enter a valid email address.';
    }

    return '';
  }, [email, submitted]);

  const passwordError = useMemo(() => {
    if (!submitted) {
      return '';
    }

    if (!password) {
      return 'Password is required.';
    }

    if (password.length < 8) {
      return 'Password must be at least 8 characters.';
    }

    return '';
  }, [password, submitted]);

  const handleCreateAccount = async () => {
    setSubmitted(true);
    setInlineError('');
    setNeedsConfirmation(false);

    if (emailError || passwordError || !email.trim() || password.length < 8) {
      return;
    }

    setLoading(true);

    try {
      const normalizedEmail = email.trim().toLowerCase();

      const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
        email: normalizedEmail,
        password,
      });

      if (signUpError) {
        throw signUpError;
      }

      const userId = signUpData?.user?.id;

      if (!userId) {
        throw new Error('Account created, but no user record was returned.');
      }

      // When email confirmation is enabled in Supabase, signUp returns a user
      // but no active session. The profile write below relies on an authenticated
      // session (RLS), so defer it and prompt the user to confirm their email.
      if (!signUpData.session) {
        setNeedsConfirmation(true);
        return;
      }

      const { error: upsertError } = await supabase.from('user_profiles').upsert(
        {
          id: userId,
          email: normalizedEmail,
          first_name: firstName,
          birth_date: birthDate,
          birth_time: birthTime,
          birth_city: city,
          birth_time_known: knowsBirthTime,
        },
        {
          onConflict: 'id',
        }
      );

      if (upsertError) {
        throw upsertError;
      }

      // No manual navigation needed: the onAuthStateChange listener in App.js
      // picks up the new session and RootNavigator swaps to the main app.
    } catch (error) {
      setInlineError(error.message || 'Something went wrong while creating your account.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.keyboard}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <ScrollView
          contentContainerStyle={styles.content}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          <Text style={styles.title}>Create your account</Text>
          <Text style={styles.subtitle}>
            Your details are saved securely so Chaya can personalise your experience every day.
          </Text>

          <TouchableOpacity activeOpacity={1} style={styles.summaryCard}>
            <Text style={styles.summaryTitle}>Your details</Text>
            <Text style={styles.summaryLine}>Name: {firstName}</Text>
            <Text style={styles.summaryLine}>Birth date: {birthDate}</Text>
            <Text style={styles.summaryLine}>Birth time: {birthTime}</Text>
            <Text style={styles.summaryLine}>Birth city: {city}</Text>
          </TouchableOpacity>

          <TouchableOpacity activeOpacity={1} style={styles.fieldGroup}>
            <Text style={styles.label}>Email</Text>
            <TextInput
              style={[styles.input, emailError ? styles.inputError : null]}
              placeholder="you@example.com"
              placeholderTextColor={palette.muted}
              autoCapitalize="none"
              autoCorrect={false}
              keyboardType="email-address"
              value={email}
              onChangeText={setEmail}
            />
            {emailError ? <Text style={styles.errorText}>{emailError}</Text> : null}
          </TouchableOpacity>

          <TouchableOpacity activeOpacity={1} style={styles.fieldGroup}>
            <Text style={styles.label}>Password</Text>
            <TextInput
              style={[styles.input, passwordError ? styles.inputError : null]}
              placeholder="Minimum 8 characters"
              placeholderTextColor={palette.muted}
              secureTextEntry
              value={password}
              onChangeText={setPassword}
            />
            {passwordError ? <Text style={styles.errorText}>{passwordError}</Text> : null}
          </TouchableOpacity>

          {inlineError ? <Text style={styles.inlineError}>{inlineError}</Text> : null}

          {needsConfirmation ? (
            <Text style={styles.confirmationText}>
              Almost there — check your email to confirm your account, then sign in to finish
              setting up Chaya.
            </Text>
          ) : null}

          <TouchableOpacity
            style={[styles.button, loading ? styles.buttonDisabled : null]}
            onPress={handleCreateAccount}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color={palette.background} />
            ) : (
              <Text style={styles.buttonText}>Create account</Text>
            )}
          </TouchableOpacity>
        </ScrollView>
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
  },
  content: {
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
    marginBottom: 24,
  },
  summaryCard: {
    backgroundColor: palette.surfaceAlt,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: palette.border,
    padding: 18,
    marginBottom: 24,
  },
  summaryTitle: {
    color: palette.goldSoft,
    fontSize: 15,
    fontWeight: '700',
    marginBottom: 10,
  },
  summaryLine: {
    color: palette.text,
    fontSize: 14,
    marginBottom: 6,
  },
  fieldGroup: {
    marginBottom: 20,
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
  inlineError: {
    color: palette.error,
    fontSize: 14,
    marginBottom: 18,
    lineHeight: 20,
  },
  confirmationText: {
    color: palette.goldSoft,
    fontSize: 14,
    marginBottom: 18,
    lineHeight: 20,
  },
  button: {
    backgroundColor: palette.gold,
    borderRadius: 16,
    paddingVertical: 18,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  buttonText: {
    color: palette.background,
    fontSize: 17,
    fontWeight: '700',
  },
});
