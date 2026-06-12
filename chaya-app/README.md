# Chaya

A daily spiritual guide app built with **Expo SDK 51** + **React Native 0.74** and React Navigation.

## Prerequisites (one-time)

- **Node.js 18 or 20 LTS** — check with `node -v` ([nodejs.org](https://nodejs.org))
- **Git**
- **Expo Go** app on your phone (App Store / Play Store), _or_ an iOS Simulator
  (Xcode, macOS) / Android Emulator (Android Studio)

## Get it running locally

```bash
# 1. Clone the repo
git clone https://github.com/michaeladane13-dotcom/aiviq-june-media.git
cd aiviq-june-media

# 2. Switch to the working branch
git checkout claude/chaya-app-codebase-JcpE2

# 3. Go into the app (it lives in this subfolder)
cd chaya-app

# 4. Install dependencies
#    --legacy-peer-deps is REQUIRED: plain `npm install` fails on the
#    onesignal-expo-plugin peer conflict against SDK 51.
npm install --legacy-peer-deps

# 5. Start the dev server
npx expo start
```

Then press **`i`** (iOS sim), **`a`** (Android emulator), or scan the QR code with
**Expo Go** on your phone.

> **Don't run plain `npm install`** — it errors out with `ERESOLVE`. Always use
> `--legacy-peer-deps`.

## What works where

- **Expo Go (easiest):** the **Welcome → Name → BirthData → Account** onboarding
  flow and the **Home** screen render fine.
- **Paywall:** does **not** work in Expo Go — `react-native-purchases` is a native
  module. For that, build a dev client: `npx expo run:ios` or `npx expo run:android`
  (requires Xcode / Android Studio).
- Auth, city autocomplete, and purchases stay inert until real keys are added in
  `constants/config.js`.

## Configuration

`constants/config.js` ships with placeholder values. Fill these in to enable the
corresponding features:

| Key                     | Used by                                   |
| ----------------------- | ----------------------------------------- |
| `SUPABASE_URL`          | Auth + `user_profiles` storage            |
| `SUPABASE_ANON_KEY`     | Auth + `user_profiles` storage            |
| `GOOGLE_PLACES_API_KEY` | Birth-city autocomplete (BirthData)       |
| `REVENUECAT_API_KEY`    | Paywall / in-app purchase (dev build)     |
| `ONESIGNAL_APP_ID`      | Push notifications (not yet wired up)      |

### Supabase

Auth + profiles expect a `user_profiles` table with columns:

```
id (uuid, PK, = auth user id), email, first_name,
birth_date (date), birth_time (time), birth_city (text),
birth_time_known (bool)
```

with Row Level Security policies allowing a user to read/write their own row.
For the smoothest dev loop, **disable email confirmation** in Supabase Auth
settings so sign-up logs you straight in.

## Project structure

```
chaya-app/
├── App.js                 # Root: session bootstrap + providers
├── app.json               # Expo config
├── constants/
│   ├── config.js          # API keys / IDs (placeholders)
│   └── palette.js          # Color palette
├── lib/
│   └── supabaseClient.js  # Supabase client (AsyncStorage-persisted session)
├── navigation/
│   └── index.js           # Onboarding vs. Main stack, driven by session
└── screens/
    ├── Home.js
    ├── Paywall.js
    └── onboarding/
        ├── Welcome.js
        ├── Name.js
        ├── BirthData.js
        └── Account.js
```

## Notes

- `onesignal-expo-plugin` is installed but currently inert (not imported, not
  registered in `app.json`). Wire it up when you add push notifications.
- Navigation between onboarding and the main app is driven by the Supabase
  session in `App.js` / `navigation/index.js` — there's no manual screen reset.
