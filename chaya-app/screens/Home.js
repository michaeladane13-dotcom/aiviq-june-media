import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  RefreshControl,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import Ionicons from 'react-native-vector-icons/Ionicons';
import palette from '../constants/palette';
import { supabase } from '../lib/supabaseClient';

function getGreeting() {
  const hour = new Date().getHours();

  if (hour < 12) {
    return 'Good morning';
  }

  if (hour < 18) {
    return 'Good afternoon';
  }

  return 'Good evening';
}

export default function Home({ navigation }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadProfile = async () => {
    try {
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (!user) {
        setProfile(null);
        return;
      }

      const { data, error } = await supabase
        .from('user_profiles')
        .select('first_name, birth_date, birth_time, birth_city, birth_time_known')
        .eq('id', user.id)
        .single();

      if (error) {
        throw error;
      }

      setProfile(data);
    } catch (error) {
      setProfile(null);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    loadProfile();
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.loadingScreen}>
        <ActivityIndicator size="large" color={palette.gold} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor={palette.gold}
          />
        }
        showsVerticalScrollIndicator={false}
      >
        <Text style={styles.greeting}>
          {getGreeting()} {profile?.first_name || 'there'}
        </Text>
        <Text style={styles.subheading}>
          Your spiritual guidance is prepared around your birth chart and daily energy.
        </Text>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Daily Insight</Text>
          <Text style={styles.cardBody}>Your insight for today is loading…</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Daily Tarot</Text>
          <Text style={styles.cardBody}>Your card of the day is loading…</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Moon Phase</Text>
          <Text style={styles.cardBody}>Current moon phase loading…</Text>
        </View>

        <TouchableOpacity style={styles.lockedCard} onPress={() => navigation.navigate('Paywall')}>
          <View style={styles.lockedHeader}>
            <Text style={[styles.cardTitle, styles.lockedTitle]}>Your Month Ahead</Text>
            <Ionicons name="lock-closed" size={20} color={palette.gold} />
          </View>
          <Text style={styles.cardBody}>
            Unlock a deeper personalised forecast with spiritual themes, intuitive guidance, and
            tarot-led reflection for the month ahead.
          </Text>
          <Text style={styles.lockedCta}>Tap to unlock</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  loadingScreen: {
    flex: 1,
    backgroundColor: palette.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
  container: {
    flex: 1,
    backgroundColor: palette.background,
  },
  content: {
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 32,
  },
  greeting: {
    color: palette.text,
    fontSize: 30,
    fontWeight: '700',
    marginBottom: 8,
  },
  subheading: {
    color: palette.muted,
    fontSize: 15,
    lineHeight: 22,
    marginBottom: 24,
  },
  card: {
    backgroundColor: palette.surface,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: palette.border,
    padding: 18,
    marginBottom: 16,
  },
  lockedCard: {
    backgroundColor: palette.surfaceAlt,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: palette.gold,
    padding: 18,
    marginTop: 4,
  },
  lockedHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  cardTitle: {
    color: palette.goldSoft,
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 8,
  },
  lockedTitle: {
    marginBottom: 0,
  },
  cardBody: {
    color: palette.text,
    fontSize: 15,
    lineHeight: 22,
  },
  lockedCta: {
    color: palette.gold,
    fontSize: 14,
    fontWeight: '700',
    marginTop: 14,
  },
});
