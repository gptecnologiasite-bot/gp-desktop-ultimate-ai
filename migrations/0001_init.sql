-- 0001_init.sql
-- Esquema inicial GP Desktop Ultimate AI (Supabase/Postgres)

create extension if not exists "pgcrypto";

-- users (perfil público vinculado a auth.users)
create table if not exists public.users (
    id uuid primary key references auth.users(id) on delete cascade,
    email text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.profiles (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    display_name text,
    avatar_url text,
    bio text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.settings (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    key text not null,
    value jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (user_id, key)
);

create table if not exists public.themes (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    name text not null,
    config jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.personalizations (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    name text not null,
    data jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.appearance_profiles (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    name text not null,
    config jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.clocks (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    name text not null,
    config jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.widgets (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    name text not null,
    config jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.wallpapers (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    name text,
    path text,
    bucket text default 'wallpapers',
    created_at timestamptz not null default now()
);

create table if not exists public.favorites (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    item_type text not null,
    item_id text not null,
    created_at timestamptz not null default now()
);

create table if not exists public.ai_history (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    prompt text,
    response text,
    model text,
    created_at timestamptz not null default now()
);

create table if not exists public.preferences (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    key text not null,
    value jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (user_id, key)
);

create table if not exists public.devices (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    device_id text not null,
    name text,
    last_seen timestamptz,
    created_at timestamptz not null default now()
);

-- Índices
create index if not exists idx_profiles_user_id on public.profiles(user_id);
create index if not exists idx_settings_user_id on public.settings(user_id);
create index if not exists idx_themes_user_id on public.themes(user_id);
create index if not exists idx_personalizations_user_id on public.personalizations(user_id);
create index if not exists idx_appearance_profiles_user_id on public.appearance_profiles(user_id);
create index if not exists idx_clocks_user_id on public.clocks(user_id);
create index if not exists idx_widgets_user_id on public.widgets(user_id);
create index if not exists idx_wallpapers_user_id on public.wallpapers(user_id);
create index if not exists idx_favorites_user_id on public.favorites(user_id);
create index if not exists idx_ai_history_user_id on public.ai_history(user_id);
create index if not exists idx_preferences_user_id on public.preferences(user_id);
create index if not exists idx_devices_user_id on public.devices(user_id);

-- RLS
alter table public.users enable row level security;
alter table public.profiles enable row level security;
alter table public.settings enable row level security;
alter table public.themes enable row level security;
alter table public.personalizations enable row level security;
alter table public.appearance_profiles enable row level security;
alter table public.clocks enable row level security;
alter table public.widgets enable row level security;
alter table public.wallpapers enable row level security;
alter table public.favorites enable row level security;
alter table public.ai_history enable row level security;
alter table public.preferences enable row level security;
alter table public.devices enable row level security;

-- Policies "own rows"
do $$
declare
    t text;
begin
    for t in select unnest(array['users','profiles','settings','themes','personalizations','appearance_profiles','clocks','widgets','wallpapers','favorites','ai_history','preferences','devices'])
    loop
        execute format('create policy "own rows select" on public.%I for select using (auth.uid() = user_id)', t);
        execute format('create policy "own rows insert" on public.%I for insert with check (auth.uid() = user_id)', t);
        execute format('create policy "own rows update" on public.%I for update using (auth.uid() = user_id) with check (auth.uid() = user_id)', t);
        execute format('create policy "own rows delete" on public.%I for delete using (auth.uid() = user_id)', t);
    end loop;
exception when duplicate_object then null;
end $$;

-- users table uses id = auth.uid()
drop policy if exists "own rows select" on public.users;
drop policy if exists "own rows insert" on public.users;
drop policy if exists "own rows update" on public.users;
drop policy if exists "own rows delete" on public.users;
create policy "own rows select" on public.users for select using (auth.uid() = id);
create policy "own rows insert" on public.users for insert with check (auth.uid() = id);
create policy "own rows update" on public.users for update using (auth.uid() = id) with check (auth.uid() = id);
create policy "own rows delete" on public.users for delete using (auth.uid() = id);
