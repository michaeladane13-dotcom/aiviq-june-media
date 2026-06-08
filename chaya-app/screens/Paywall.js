import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import Purchases from 'react-native-purchases';
import palette from '../constants/palette';
import { REVENUECAT_API_KEY } from '../constants/config';

export default function Paywall() {
  const [loading, setLoading] = useState(false);
  const [offeringsLoading, setOfferingsLoading] = useState(true);
  const [purchaseSuccess, setPurchaseSuccess] = useState(false);
  const [inlineError, setInlineError] = useState('');
  const [selectedPackage, setSelectedPackage] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const initializePurchases = async () => {
      try {
        await Purchases.configure({ apiKey: REVENUECAT_API_KEY });
        const offerings = await Purchases.getOfferings();
        const currentPackage = offerings.current?.availablePackages?.[0] || null;

        if (isMounted) {
          setSelectedPackage(currentPackage);
        }
      } catch (error) {
        if (isMounted) {
          setInlineError(error.message || 'Unable to load purchase options right now.');
        }
      } finally {
        if (isMounted) {
          setOfferingsLoading(false);
        }
      }
    };

    initializePurchases();

    return () => {
      isMounted = false;
    };
  }, []);

  const handlePurchase = async () => {
    setLoading(true);
    setInlineError('');
    setPurchaseSuccess(false);

    try {
      if (!selectedPackage) {
        throw new Error('No purchase package is currently available.');
      }

      await Purchases.purchasePackage(selectedPackage);
      setPurchaseSuccess(true);
    } catch (error) {
      if (!error.userCancelled) {
        setInlineError(error.message || 'Purchase failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.heroCard}>
          <Text style={styles.title}>Your Month Ahead</Text>
          <Text style={styles.subtitle}>
            Receive a deeper monthly report designed around your energy, spiritual themes, and
            intuitive guidance.
          </Text>
        </View>

        <View style={styles.featureCard}>
          <Text style={styles.featureHeading}>What’s included</Text>
          <Text style={styles.featureItem}>• A personalised energetic overview for the month</Text>
          <Text style={styles.featureItem}>• Tarot themes and intuitive guidance from Chaya</Text>
          <Text style={styles.featureItem}>• Reflection points for love, purpose, and growth</Text>
          <Text style={styles.featureItem}>• One-time unlock for $14.99</Text>
        </View>

        <View style={styles.priceCard}>
          <Text style={styles.priceLabel}>One-time purchase</Text>
          <Text style={styles.price}>$14.99</Text>
        </View>

        {offeringsLoading ? (
          <View style={styles.loadingWrap}>
            <ActivityIndicator color={palette.gold} />
          </View>
        ) : null}

        {inlineError ? <Text style={styles.errorText}>{inlineError}</Text> : null}

        {purchaseSuccess ? (
          <Text style={styles.successText}>
            Your Month Ahead has been unlocked successfully.
          </Text>
        ) : null}

        <TouchableOpacity
          style={[styles.button, (loading || offeringsLoading) ? styles.buttonDisabled : null]}
          onPress={handlePurchase}
          disabled={loading || offeringsLoading}
        >
          {loading ? (
            <ActivityIndicator color={palette.background} />
          ) : (
            <Text style={styles.buttonText}>Unlock for $14.99</Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: palette.background,
  },
  content: {
    paddingHorizontal: 24,
    paddingTop: 28,
    paddingBottom: 32,
  },
  heroCard: {
    backgroundColor: palette.surfaceAlt,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: palette.gold,
    padding: 22,
    marginBottom: 20,
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
  },
  featureCard: {
    backgroundColor: palette.surface,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: palette.border,
    padding: 20,
    marginBottom: 20,
  },
  featureHeading: {
    color: palette.goldSoft,
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 14,
  },
  featureItem: {
    color: palette.text,
    fontSize: 15,
    lineHeight: 24,
    marginBottom: 8,
  },
  priceCard: {
    backgroundColor: palette.surface,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: palette.border,
    padding: 20,
    alignItems: 'center',
    marginBottom: 24,
  },
  priceLabel: {
    color: palette.muted,
    fontSize: 14,
    marginBottom: 8,
  },
  price: {
    color: palette.gold,
    fontSize: 36,
    fontWeight: '700',
  },
  loadingWrap: {
    alignItems: 'center',
    marginBottom: 16,
  },
  errorText: {
    color: palette.error,
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 14,
    textAlign: 'center',
  },
  successText: {
    color: palette.goldSoft,
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 14,
    textAlign: 'center',
  },
  button: {
    backgroundColor: palette.gold,
    borderRadius: 16,
    paddingVertical: 18,
    alignItems: 'center',
    justifyContent: 'center',
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
