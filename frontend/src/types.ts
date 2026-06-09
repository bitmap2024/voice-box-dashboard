export type Role = {
  id: string;
  name: string;
  code: string;
  permissions: string[];
};

export type Factory = {
  id: string;
  name: string;
  industry: string;
  status: string;
  plan_type: string;
  device_quota: number;
  created_at: string;
};

export type User = {
  id: string;
  factory_id: string | null;
  name: string;
  email: string;
  phone?: string;
  role_code: string;
  status: string;
  last_login_at?: string;
  role: Role;
  factory?: Factory | null;
};

export type EndUser = {
  id: string;
  factory_id: string;
  factory_name?: string | null;
  device_id: string | null;
  device_sn?: string | null;
  nickname: string;
  age_range?: string | null;
  region?: string | null;
  user_segment?: string | null;
  bound_at?: string | null;
  last_active_at?: string | null;
  total_conversations: number;
};

export type Device = {
  id: string;
  factory_id: string;
  sn: string;
  mac_address: string;
  model: string;
  firmware_version: string;
  batch_no: string;
  status: string;
  activated_at?: string | null;
  last_seen_at?: string | null;
  current_character_id?: string | null;
  wifi_rssi: number;
  rtt_ms: number;
  today_conversations: number;
  abnormal: boolean;
  bound_user?: EndUser | null;
};

export type Character = {
  id: string;
  factory_id: string;
  name: string;
  scene_type: string;
  age_range: string;
  tone_style: string;
  description: string;
  status: string;
  current_prompt_version_id?: string | null;
  bound_device_count: number;
  today_conversations: number;
  fallback_rate: number;
  avg_latency_ms: number;
};

export type PromptVersion = {
  id: string;
  factory_id: string;
  character_id: string;
  version: string;
  system_prompt: string;
  structured_config: Record<string, unknown>;
  change_note: string;
  status: string;
  created_by: string;
  created_at: string;
  published_at?: string | null;
};

export type Conversation = {
  id: string;
  factory_id: string;
  factory_name?: string;
  device_id: string;
  character_id: string;
  device_sn?: string;
  character_name?: string;
  bound_user?: EndUser | null;
  anonymous_session_id: string;
  anonymous_user_label?: string;
  user_segment?: string;
  started_at: string;
  ended_at: string;
  total_turns: number;
  success: boolean;
  total_latency_ms: number;
  feedback?: string;
  turns?: ConversationTurn[];
};

export type ConversationTurn = {
  id: string;
  trace_id: string;
  user_asr_text: string;
  ai_reply_text: string;
  intent: string;
  fallback_hit: boolean;
  safety_hit: boolean;
  success: boolean;
  error_code?: string | null;
  latency_total_ms: number;
  e2e_first_response_ms?: number | null;
  llm_context?: string;
  created_at: string;
  device_sn?: string;
  character_name?: string;
  badcase_type?: string;
};

export type PaginatedResponse<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
};

export type Alert = {
  id: string;
  device_id: string;
  device_sn?: string;
  alert_type: string;
  severity: string;
  title: string;
  content: string;
  status: string;
  created_at: string;
  resolved_at?: string | null;
};

export type Kpi = {
  label: string;
  value: string | number;
  unit: string;
  trend: string;
};
