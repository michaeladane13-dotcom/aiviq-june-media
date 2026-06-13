-- Chaya — initial schema
-- Privacy model: raw birth PII lives ONLY in user_profiles (RLS-locked to the
-- owner). Charts are computed server-side (Edge Function) by our own ephemeris.
-- The LLM (Kimi) only ever receives the finished chart JSON + a prompt — never
-- the user's name, birth time, or birth place, and never via the client.
--
-- Content tables (natal_charts, daily_content, monthly_reports, entitlements)
-- are written by Edge Functions using the service-role key, which bypasses RLS.
-- End users get READ-ONLY access to their own rows; they cannot write content.

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- updated_at helper
-- ---------------------------------------------------------------------------
create or replace function set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- ---------------------------------------------------------------------------
-- user_profiles  — matches the columns the app already upserts in Account.js,
-- plus resolved location/timezone needed for an exact chart.
-- ---------------------------------------------------------------------------
create table if not exists user_profiles (
  id               uuid primary key references auth.users(id) on delete cascade,
  email            text,
  first_name       text not null,
  birth_date       date not null,
  birth_time       time,                       -- null when birth_time_known = false
  birth_time_known boolean not null default true,
  birth_city       text not null,
  -- resolved from Google Places when available; required for an exact chart
  birth_lat        double precision,
  birth_lon        double precision,
  birth_tz         text,                        -- IANA zone, e.g. 'Europe/London'
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);

drop trigger if exists trg_user_profiles_updated on user_profiles;
create trigger trg_user_profiles_updated
  before update on user_profiles
  for each row execute function set_updated_at();

alter table user_profiles enable row level security;

create policy "profiles: owner can read"
  on user_profiles for select using (auth.uid() = id);
create policy "profiles: owner can insert"
  on user_profiles for insert with check (auth.uid() = id);
create policy "profiles: owner can update"
  on user_profiles for update using (auth.uid() = id) with check (auth.uid() = id);

-- ---------------------------------------------------------------------------
-- natal_charts — the computed chart (Swiss Ephemeris). One per user per house
-- system. `chart` holds the full position/house/aspect payload as JSON so the
-- content layer and the UI read identical numbers.
-- ---------------------------------------------------------------------------
create table if not exists natal_charts (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null references auth.users(id) on delete cascade,
  house_system   text not null default 'placidus',
  chart          jsonb not null,
  engine_version text not null,                 -- e.g. 'sweph-2.10'
  computed_at    timestamptz not null default now(),
  unique (user_id, house_system)
);

alter table natal_charts enable row level security;
create policy "charts: owner can read"
  on natal_charts for select using (auth.uid() = user_id);

-- ---------------------------------------------------------------------------
-- daily_content — the free daily cards (insight / tarot). Moon phase is
-- computed client/server-side and not stored here. One row per user/day/kind.
-- ---------------------------------------------------------------------------
create table if not exists daily_content (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  for_date    date not null,
  kind        text not null check (kind in ('insight','tarot')),
  body        text not null,
  model       text,                             -- e.g. 'kimi-k2.5'
  created_at  timestamptz not null default now(),
  unique (user_id, for_date, kind)
);

alter table daily_content enable row level security;
create policy "daily: owner can read"
  on daily_content for select using (auth.uid() = user_id);

-- ---------------------------------------------------------------------------
-- monthly_reports — the paid "Your Month Ahead". `period` is 'YYYY-MM'.
-- ---------------------------------------------------------------------------
create table if not exists monthly_reports (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  period      text not null,                    -- 'YYYY-MM'
  body        text not null,
  model       text,
  created_at  timestamptz not null default now(),
  unique (user_id, period)
);

alter table monthly_reports enable row level security;
create policy "reports: owner can read"
  on monthly_reports for select using (auth.uid() = user_id);

-- ---------------------------------------------------------------------------
-- entitlements — mirror of RevenueCat purchases so the app can gate the paid
-- report without a network round-trip. RevenueCat webhook → Edge Function
-- writes here (service role). Product 'month_ahead' is the one-time $14.99.
-- ---------------------------------------------------------------------------
create table if not exists entitlements (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  product     text not null,                    -- 'month_ahead'
  period      text,                             -- the month it unlocked, 'YYYY-MM'
  source      text not null default 'revenuecat',
  active      boolean not null default true,
  granted_at  timestamptz not null default now(),
  unique (user_id, product, period)
);

alter table entitlements enable row level security;
create policy "entitlements: owner can read"
  on entitlements for select using (auth.uid() = user_id);
