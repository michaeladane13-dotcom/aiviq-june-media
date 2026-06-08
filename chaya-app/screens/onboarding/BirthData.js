import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';
import { GooglePlacesAutocomplete } from 'react-native-google-places-autocomplete';
import palette from '../../constants/palette';
import { GOOGLE_PLACES_API_KEY } from '../../constants/config';

function formatDateForDisplay(date) {
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function formatDateForStorage(date) {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, '0');
  const day = `${date.getDate()}`.padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function formatTimeForDisplay(date) {
  return date.toLocaleTimeString([], {
    hour: 'numeric',
    minute: '2-digit',
  });
}

function formatTimeForStorage(date) {
  const hours = `${date.getHours()}`.padStart(2, '0');
  const minutes = `${date.getMinutes()}`.padStart(2, '0');
  const seconds = '00';
  return `${hours}:${minutes}:${seconds}`;
}

export default function BirthData({ navigation, route }) {
  const { firstName } = route.params;
  const placesRef = useRef(null);

  const defaultNoon = useMemo(() => {
    const date = new Date();
    date.setHours(12, 0, 0, 0);
    return date;
  }, []);

  const [birthDate, setBirthDate] = useState(new Date());
  const [birthTime, setBirthTime] = useState(defaultNoon);
  const [knowsBirthTime, setKnowsBirthTime] = useState(true);
  const [birthCity, setBirthCity] = useState('');
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    if (!knowsBirthTime) {
      setBirthTime(defaultNoon);
    }
  }, [defaultNoon, knowsBirthTime]);

  const dateError = submitted && !birthDate ? 'Please select your birth date.' : '';
  const cityError = submitted && !birthCity.trim() ? 'Please select your birth city.' : '';

  const handleDateChange = (event, selectedDate) => {
    if (Platform.OS !== 'ios') {
      setShowDatePicker(false);
    }

    if (selectedDate) {
      setBirthDate(selectedDate);
    }
  };

  const handleTimeChange = (event, selectedTime) => {
    if (Platform.OS !== 'ios') {
      setShowTimePicker(false);
    }

    if (selectedTime) {
      setBirthTime(selectedTime);
    }
  };

  const handleNext = () => {
    setSubmitted(true);

    if (!birthDate || !birthCity.trim()) {
      return;
    }

    navigation.navigate('Account', {
      firstName,
      birthDate: formatDateForStorage(birthDate),
      birthTime: formatTimeForStorage(knowsBirthTime ? birthTime : defaultNoon),
      knowsBirthTime,
      city: birthCity.trim(),
    });
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.keyboard}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <ScrollView
          style={styles.scroll}
          contentContainerStyle={styles.content}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          <Text style={styles.title}>Your birth details</Text>
          <Text style={styles.subtitle}>
            These details help Chaya personalise your spiritual guidance each day.
          </Text>

          <View style={styles.fieldGroup}>
            <Text style={styles.label}>Birth date</Text>
            <TouchableOpacity
              style={[styles.selector, dateError ? styles.selectorError : null]}
              onPress={() => setShowDatePicker(true)}
            >
              <Text style={styles.selectorText}>{formatDateForDisplay(birthDate)}</Text>
            </TouchableOpacity>
            {dateError ? <Text style={styles.errorText}>{dateError}</Text> : null}
          </View>

          <View style={styles.fieldGroup}>
            <View style={styles.toggleRow}>
              <Text style={styles.label}>Birth time</Text>
              <View style={styles.toggleWrap}>
                <Text style={styles.toggleText}>I don’t know</Text>
                <Switch
                  value={!knowsBirthTime}
                  onValueChange={(value) => setKnowsBirthTime(!value)}
                  trackColor={{ false: palette.purple, true: palette.border }}
                  thumbColor={!knowsBirthTime ? palette.gold : palette.goldSoft}
                />
              </View>
            </View>

            <TouchableOpacity
              style={[
                styles.selector,
                !knowsBirthTime ? styles.selectorDisabled : null,
              ]}
              onPress={() => {
                if (knowsBirthTime) {
                  setShowTimePicker(true);
                }
              }}
              activeOpacity={knowsBirthTime ? 0.85 : 1}
            >
              <Text
                style={[
                  styles.selectorText,
                  !knowsBirthTime ? styles.selectorTextMuted : null,
                ]}
              >
                {knowsBirthTime ? formatTimeForDisplay(birthTime) : '12:00 PM'}
              </Text>
            </TouchableOpacity>
          </View>

          <View style={[styles.fieldGroup, styles.cityGroup]}>
            <Text style={styles.label}>Birth city</Text>
            <View style={[styles.cityAutocompleteWrap, cityError ? styles.selectorError : null]}>
              <GooglePlacesAutocomplete
                ref={placesRef}
                placeholder="Search for your birth city"
                fetchDetails={true}
                enablePoweredByContainer={false}
                textInputProps={{
                  placeholderTextColor: palette.muted,
                }}
                onPress={(data, details = null) => {
                  const cityName =
                    details?.address_components?.find((component) =>
                      component.types.includes('locality')
                    )?.long_name ||
                    details?.address_components?.find((component) =>
                      component.types.includes('administrative_area_level_1')
                    )?.long_name ||
                    data.structured_formatting?.main_text ||
                    data.description;

                  setBirthCity(cityName);
                }}
                query={{
                  key: GOOGLE_PLACES_API_KEY,
                  language: 'en',
                  types: '(cities)',
                }}
                nearbyPlacesAPI="GooglePlacesSearch"
                debounce={250}
                styles={{
                  container: styles.googleContainer,
                  textInputContainer: styles.googleTextInputContainer,
                  textInput: styles.googleTextInput,
                  listView: styles.googleListView,
                  row: styles.googleRow,
                  description: styles.googleDescription,
                  separator: styles.googleSeparator,
                }}
              />
            </View>
            {birthCity ? <Text style={styles.selectedCity}>Selected city: {birthCity}</Text> : null}
            {cityError ? <Text style={styles.errorText}>{cityError}</Text> : null}
          </View>
        </ScrollView>

        <View style={styles.footer}>
          <TouchableOpacity style={styles.button} onPress={handleNext}>
            <Text style={styles.buttonText}>Next</Text>
          </TouchableOpacity>
        </View>

        {showDatePicker ? (
          <DateTimePicker
            value={birthDate || new Date()}
            mode="date"
            display={Platform.OS === 'ios' ? 'spinner' : 'default'}
            maximumDate={new Date()}
            onChange={handleDateChange}
          />
        ) : null}

        {showTimePicker && knowsBirthTime ? (
          <DateTimePicker
            value={birthTime}
            mode="time"
            display={Platform.OS === 'ios' ? 'spinner' : 'default'}
            onChange={handleTimeChange}
          />
        ) : null}
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
  scroll: {
    flex: 1,
  },
  content: {
    paddingHorizontal: 24,
    paddingTop: 48,
    paddingBottom: 24,
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
    marginBottom: 22,
  },
  cityGroup: {
    zIndex: 20,
  },
  label: {
    color: palette.goldSoft,
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 10,
  },
  selector: {
    backgroundColor: palette.surface,
    borderColor: palette.border,
    borderWidth: 1,
    borderRadius: 16,
    minHeight: 56,
    paddingHorizontal: 16,
    justifyContent: 'center',
  },
  selectorDisabled: {
    opacity: 0.65,
  },
  selectorText: {
    color: palette.text,
    fontSize: 16,
  },
  selectorTextMuted: {
    color: palette.muted,
  },
  selectorError: {
    borderColor: palette.error,
  },
  errorText: {
    color: palette.error,
    fontSize: 13,
    marginTop: 8,
  },
  toggleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  toggleWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  toggleText: {
    color: palette.muted,
    fontSize: 13,
  },
  cityAutocompleteWrap: {
    borderWidth: 1,
    borderColor: palette.border,
    borderRadius: 16,
    overflow: 'hidden',
    backgroundColor: palette.surface,
  },
  googleContainer: {
    flex: 0,
  },
  googleTextInputContainer: {
    backgroundColor: palette.surface,
    borderTopWidth: 0,
    borderBottomWidth: 0,
    paddingHorizontal: 0,
  },
  googleTextInput: {
    backgroundColor: palette.surface,
    color: palette.text,
    height: 56,
    fontSize: 16,
    marginTop: 0,
    marginBottom: 0,
    borderRadius: 0,
    paddingHorizontal: 16,
  },
  googleListView: {
    backgroundColor: palette.surfaceAlt,
    borderTopWidth: 1,
    borderTopColor: palette.border,
  },
  googleRow: {
    backgroundColor: palette.surfaceAlt,
    paddingVertical: 14,
    paddingHorizontal: 16,
  },
  googleDescription: {
    color: palette.text,
    fontSize: 15,
  },
  googleSeparator: {
    height: 1,
    backgroundColor: palette.border,
  },
  selectedCity: {
    color: palette.goldSoft,
    fontSize: 13,
    marginTop: 8,
  },
  footer: {
    paddingHorizontal: 24,
    paddingBottom: 32,
    paddingTop: 8,
    backgroundColor: palette.background,
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
