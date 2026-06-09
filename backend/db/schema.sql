create extension if not exists "uuid-ossp";

create type factory_status as enum ('trial', 'active', 'suspended');
create type account_status as enum ('active', 'disabled');
create type device_status as enum ('online', 'offline', 'warning', 'disabled');
create type prompt_status as enum ('draft', 'published', 'archived');
create type alert_status as enum ('open', 'resolved', 'ignored');
create type severity_level as enum ('low', 'medium', 'high', 'critical');

create table factories (
  id uuid primary key default uuid_generate_v4(),
  name varchar(120) not null,
  industry varchar(80) not null default 'AI 玩具',
  status factory_status not null default 'trial',
  plan_type varchar(40) not null default 'Trial',
  device_quota integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table roles (
  id uuid primary key default uuid_generate_v4(),
  factory_id uuid references factories(id) on delete cascade,
  code varchar(60) not null,
  name varchar(80) not null,
  description text,
  is_system boolean not null default false,
  created_at timestamptz not null default now(),
  unique(factory_id, code)
);

create table permissions (
  id uuid primary key default uuid_generate_v4(),
  code varchar(80) not null unique,
  name varchar(80) not null,
  module varchar(60) not null
);

create table role_permissions (
  role_id uuid not null references roles(id) on delete cascade,
  permission_id uuid not null references permissions(id) on delete cascade,
  primary key (role_id, permission_id)
);

create table admin_users (
  id uuid primary key default uuid_generate_v4(),
  factory_id uuid references factories(id) on delete cascade,
  role_id uuid not null references roles(id),
  name varchar(80) not null,
  email varchar(160) not null unique,
  phone varchar(40),
  password_hash varchar(255) not null,
  status account_status not null default 'active',
  last_login_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table ai_characters (
  id uuid primary key default uuid_generate_v4(),
  factory_id uuid not null references factories(id) on delete cascade,
  name varchar(120) not null,
  avatar_url text,
  description text,
  scene_type varchar(80) not null,
  age_range varchar(60),
  tone_style varchar(120),
  status prompt_status not null default 'draft',
  current_prompt_version_id uuid,
  created_by uuid references admin_users(id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table prompt_versions (
  id uuid primary key default uuid_generate_v4(),
  factory_id uuid not null references factories(id) on delete cascade,
  character_id uuid not null references ai_characters(id) on delete cascade,
  version varchar(40) not null,
  system_prompt text not null,
  structured_config jsonb not null default '{}'::jsonb,
  change_note text,
  status prompt_status not null default 'draft',
  created_by uuid references admin_users(id),
  created_at timestamptz not null default now(),
  published_at timestamptz,
  unique(character_id, version)
);

alter table ai_characters
  add constraint fk_ai_characters_current_prompt
  foreign key (current_prompt_version_id) references prompt_versions(id);

create table devices (
  id uuid primary key default uuid_generate_v4(),
  factory_id uuid not null references factories(id) on delete cascade,
  sn varchar(80) not null unique,
  mac_address varchar(80) not null,
  model varchar(80) not null,
  firmware_version varchar(40) not null,
  batch_no varchar(80),
  status device_status not null default 'offline',
  current_character_id uuid references ai_characters(id),
  activated_at timestamptz,
  last_seen_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table device_bindings (
  id uuid primary key default uuid_generate_v4(),
  factory_id uuid not null references factories(id) on delete cascade,
  device_id uuid not null references devices(id) on delete cascade,
  sn varchar(80) not null,
  bind_status varchar(40) not null default 'bound',
  bound_by uuid references admin_users(id),
  bound_at timestamptz not null default now(),
  unbound_at timestamptz
);

create table conversations (
  id uuid primary key default uuid_generate_v4(),
  factory_id uuid not null references factories(id) on delete cascade,
  device_id uuid not null references devices(id),
  character_id uuid references ai_characters(id),
  anonymous_session_id varchar(120),
  anonymous_user_label varchar(120),
  user_segment varchar(80),
  started_at timestamptz not null,
  ended_at timestamptz,
  total_turns integer not null default 0,
  success boolean not null default true,
  total_latency_ms integer,
  feedback varchar(40),
  created_at timestamptz not null default now()
);

create table conversation_turns (
  id uuid primary key default uuid_generate_v4(),
  factory_id uuid not null references factories(id) on delete cascade,
  conversation_id uuid not null references conversations(id) on delete cascade,
  device_id uuid not null references devices(id),
  character_id uuid references ai_characters(id),
  prompt_version_id uuid references prompt_versions(id),
  trace_id varchar(120) not null unique,
  user_asr_text text,
  ai_reply_text text,
  intent varchar(120),
  fallback_hit boolean not null default false,
  safety_hit boolean not null default false,
  success boolean not null default true,
  error_code varchar(120),
  audio_input_url text,
  audio_output_url text,
  latency_total_ms integer,
  created_at timestamptz not null default now()
);

create table latency_traces (
  id uuid primary key default uuid_generate_v4(),
  factory_id uuid not null references factories(id) on delete cascade,
  device_id uuid not null references devices(id),
  conversation_turn_id uuid not null unique references conversation_turns(id) on delete cascade,
  trace_id varchar(120) not null unique,
  vad_ms integer,
  upload_ms integer,
  asr_ms integer,
  llm_ttft_ms integer,
  llm_total_ms integer,
  tts_first_audio_ms integer,
  tts_total_ms integer,
  playback_start_ms integer,
  e2e_first_response_ms integer,
  created_at timestamptz not null default now()
);

create table device_telemetry (
  id bigserial primary key,
  factory_id uuid not null references factories(id) on delete cascade,
  device_id uuid not null references devices(id) on delete cascade,
  sn varchar(80) not null,
  ts timestamptz not null,
  online boolean not null,
  wifi_rssi integer,
  websocket_connected boolean,
  rtt_ms integer,
  reconnect_count integer not null default 0,
  upload_fail_count integer not null default 0,
  playback_fail_count integer not null default 0,
  firmware_version varchar(40),
  free_memory integer,
  cpu_usage numeric(5,2),
  reboot_reason varchar(120),
  audio_state varchar(40)
);

create table device_events (
  id uuid primary key default uuid_generate_v4(),
  factory_id uuid not null references factories(id) on delete cascade,
  device_id uuid not null references devices(id) on delete cascade,
  event_type varchar(80) not null,
  severity severity_level not null default 'low',
  payload jsonb not null default '{}'::jsonb,
  occurred_at timestamptz not null default now()
);

create table alerts (
  id uuid primary key default uuid_generate_v4(),
  factory_id uuid not null references factories(id) on delete cascade,
  device_id uuid references devices(id) on delete set null,
  alert_type varchar(80) not null,
  severity severity_level not null,
  title varchar(160) not null,
  content text not null,
  status alert_status not null default 'open',
  created_at timestamptz not null default now(),
  resolved_at timestamptz,
  resolved_by uuid references admin_users(id)
);

create table badcases (
  id uuid primary key default uuid_generate_v4(),
  factory_id uuid not null references factories(id) on delete cascade,
  conversation_turn_id uuid not null references conversation_turns(id) on delete cascade,
  badcase_type varchar(80) not null,
  reason text,
  status varchar(40) not null default 'open',
  marked_by uuid references admin_users(id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table factory_daily_metrics (
  id bigserial primary key,
  factory_id uuid not null references factories(id) on delete cascade,
  metric_date date not null,
  active_device_count integer not null default 0,
  online_rate numeric(6,3),
  conversation_count integer not null default 0,
  avg_turns numeric(8,2),
  success_rate numeric(6,3),
  fallback_rate numeric(6,3),
  p50_first_response_ms integer,
  p90_first_response_ms integer,
  p95_first_response_ms integer,
  asr_fail_rate numeric(6,3),
  tts_fail_rate numeric(6,3),
  llm_fail_rate numeric(6,3),
  cloud_cost_estimate numeric(12,4),
  unique(factory_id, metric_date)
);

create table industry_daily_benchmarks (
  id bigserial primary key,
  industry varchar(80) not null,
  metric_date date not null,
  metric_name varchar(80) not null,
  avg_value numeric(14,4),
  median_value numeric(14,4),
  p75_value numeric(14,4),
  p90_value numeric(14,4),
  top25_value numeric(14,4),
  sample_factory_count integer not null,
  created_at timestamptz not null default now(),
  unique(industry, metric_date, metric_name)
);

create table recommendations (
  id uuid primary key default uuid_generate_v4(),
  factory_id uuid not null references factories(id) on delete cascade,
  recommendation_type varchar(80) not null,
  severity severity_level not null default 'medium',
  title varchar(160) not null,
  content text not null,
  evidence jsonb not null default '{}'::jsonb,
  status varchar(40) not null default 'open',
  created_at timestamptz not null default now(),
  resolved_at timestamptz
);

create table audit_logs (
  id bigserial primary key,
  factory_id uuid references factories(id) on delete cascade,
  admin_user_id uuid references admin_users(id) on delete set null,
  action varchar(120) not null,
  target_type varchar(80),
  target_id varchar(120),
  ip varchar(80),
  user_agent text,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index idx_admin_users_factory on admin_users(factory_id);
create index idx_devices_factory_status on devices(factory_id, status);
create index idx_devices_factory_firmware on devices(factory_id, firmware_version);
create index idx_devices_last_seen on devices(factory_id, last_seen_at desc);
create index idx_characters_factory on ai_characters(factory_id, status);
create index idx_prompt_versions_character on prompt_versions(character_id, created_at desc);
create index idx_conversations_factory_time on conversations(factory_id, started_at desc);
create index idx_conversations_device_time on conversations(factory_id, device_id, started_at desc);
create index idx_turns_factory_time on conversation_turns(factory_id, created_at desc);
create index idx_turns_trace on conversation_turns(trace_id);
create index idx_latency_factory_time on latency_traces(factory_id, created_at desc);
create index idx_telemetry_device_ts on device_telemetry(factory_id, device_id, ts desc);
create index idx_events_device_time on device_events(factory_id, device_id, occurred_at desc);
create index idx_alerts_factory_status on alerts(factory_id, status, created_at desc);
create index idx_badcases_factory_status on badcases(factory_id, status, created_at desc);
create index idx_factory_daily_metrics_date on factory_daily_metrics(metric_date desc);
create index idx_industry_benchmark_date on industry_daily_benchmarks(industry, metric_date desc);
