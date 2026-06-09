roles = [
    {"id": "role_super", "name": "平台管理员", "code": "super_admin", "permissions": ["*"]},
    {"id": "role_admin", "name": "工厂管理员", "code": "factory_admin", "permissions": ["dashboard:read", "device:*", "character:*", "conversation:read", "user:*", "industry:read", "alert:*"]},
    {"id": "role_ops", "name": "运营人员", "code": "operator", "permissions": ["dashboard:read", "character:*", "conversation:read", "industry:read"]},
    {"id": "role_engineer", "name": "工程人员", "code": "engineer", "permissions": ["dashboard:read", "device:*", "conversation:trace", "alert:*"]},
    {"id": "role_readonly", "name": "只读账号", "code": "readonly", "permissions": ["dashboard:read", "device:read", "character:read", "conversation:read", "industry:read"]},
]

factories = [
    {"id": "fac_a", "name": "星河 AI 玩具工厂", "industry": "AI 玩具", "status": "active", "plan_type": "Enterprise", "device_quota": 12000, "created_at": "2026-04-18T09:00:00Z"},
    {"id": "fac_b", "name": "云朵儿童硬件", "industry": "AI 玩具", "status": "active", "plan_type": "Professional", "device_quota": 6000, "created_at": "2026-05-02T09:00:00Z"},
    {"id": "fac_c", "name": "小鹿陪伴机器人", "industry": "AI 玩具", "status": "trial", "plan_type": "Trial", "device_quota": 500, "created_at": "2026-05-20T09:00:00Z"},
]

admin_users = [
    {"id": "u_super", "factory_id": None, "name": "平台管理员", "email": "admin@voicebox.ai", "phone": "13800000000", "role_code": "super_admin", "status": "active", "last_login_at": "2026-06-09T08:30:00Z", "password": "123456"},
    {"id": "u_a_admin", "factory_id": "fac_a", "name": "王敏", "email": "factory-a@voicebox.ai", "phone": "13900000001", "role_code": "factory_admin", "status": "active", "last_login_at": "2026-06-09T08:40:00Z", "password": "123456"},
    {"id": "u_engineer", "factory_id": "fac_a", "name": "陈工", "email": "engineer@voicebox.ai", "phone": "13900000002", "role_code": "engineer", "status": "active", "last_login_at": "2026-06-09T08:18:00Z", "password": "123456"},
    {"id": "u_b_admin", "factory_id": "fac_b", "name": "李娜", "email": "factory-b@voicebox.ai", "phone": "13900000003", "role_code": "factory_admin", "status": "active", "last_login_at": "2026-06-08T20:18:00Z", "password": "123456"},
]

characters = [
    {"id": "char_bear", "factory_id": "fac_a", "name": "小熊老师", "scene_type": "英语陪练", "age_range": "4-8 岁", "tone_style": "温柔、鼓励", "description": "面向儿童的英语启蒙角色", "status": "published", "current_prompt_version_id": "pv_bear_2", "bound_device_count": 4120, "today_conversations": 32860, "fallback_rate": 0.071, "avg_latency_ms": 1420},
    {"id": "char_story", "factory_id": "fac_a", "name": "睡前故事姐姐", "scene_type": "故事陪伴", "age_range": "3-7 岁", "tone_style": "轻柔、耐心", "description": "讲故事并引导孩子表达", "status": "published", "current_prompt_version_id": "pv_story_1", "bound_device_count": 2840, "today_conversations": 22930, "fallback_rate": 0.102, "avg_latency_ms": 1810},
    {"id": "char_dino", "factory_id": "fac_b", "name": "恐龙探险家", "scene_type": "百科问答", "age_range": "5-10 岁", "tone_style": "活泼、探索", "description": "恐龙主题知识探索", "status": "published", "current_prompt_version_id": "pv_dino_1", "bound_device_count": 1630, "today_conversations": 9180, "fallback_rate": 0.128, "avg_latency_ms": 2120},
]

prompt_versions = [
    {"id": "pv_bear_1", "factory_id": "fac_a", "character_id": "char_bear", "version": "v1.0", "system_prompt": "你是一个温柔的儿童英语老师。", "structured_config": {"role_identity": "儿童英语老师", "reply_length": "30 字以内", "active_guidance": True}, "change_note": "初始版本", "status": "archived", "created_by": "王敏", "created_at": "2026-05-01T10:00:00Z", "published_at": "2026-05-01T10:20:00Z"},
    {"id": "pv_bear_2", "factory_id": "fac_a", "character_id": "char_bear", "version": "v1.1", "system_prompt": "你是一个温柔、鼓励式的儿童英语陪练老师。回复要短，适合 4-8 岁儿童。", "structured_config": {"role_identity": "儿童英语陪练老师", "reply_length": "2 句话以内", "active_guidance": True, "forbidden_topics": ["暴力", "成人内容"]}, "change_note": "缩短回复并加强鼓励语气", "status": "published", "created_by": "王敏", "created_at": "2026-05-18T10:00:00Z", "published_at": "2026-05-18T10:20:00Z"},
    {"id": "pv_story_1", "factory_id": "fac_a", "character_id": "char_story", "version": "v1.0", "system_prompt": "你是睡前故事姐姐，用轻柔语言讲短故事。", "structured_config": {"role_identity": "睡前故事陪伴", "reply_length": "80 字以内", "active_guidance": False}, "change_note": "初始上线", "status": "published", "created_by": "王敏", "created_at": "2026-05-04T10:00:00Z", "published_at": "2026-05-04T11:00:00Z"},
    {"id": "pv_dino_1", "factory_id": "fac_b", "character_id": "char_dino", "version": "v1.0", "system_prompt": "你是恐龙探险家，带孩子探索恐龙知识。", "structured_config": {"role_identity": "恐龙百科伙伴", "reply_length": "60 字以内", "active_guidance": True}, "change_note": "初始上线", "status": "published", "created_by": "李娜", "created_at": "2026-05-10T10:00:00Z", "published_at": "2026-05-10T11:00:00Z"},
]

devices = [
    {"id": "dev_001", "factory_id": "fac_a", "sn": "VB202606090001", "mac_address": "A4:CF:12:11:20:01", "model": "VB-ESP32-S3", "firmware_version": "1.0.7", "batch_no": "B202606", "status": "online", "activated_at": "2026-06-01T09:00:00Z", "last_seen_at": "2026-06-09T08:58:00Z", "current_character_id": "char_bear", "wifi_rssi": -62, "rtt_ms": 76, "today_conversations": 54, "abnormal": False},
    {"id": "dev_002", "factory_id": "fac_a", "sn": "VB202606090002", "mac_address": "A4:CF:12:11:20:02", "model": "VB-ESP32-S3", "firmware_version": "1.0.5", "batch_no": "B202606", "status": "warning", "activated_at": "2026-06-02T09:00:00Z", "last_seen_at": "2026-06-09T08:51:00Z", "current_character_id": "char_story", "wifi_rssi": -81, "rtt_ms": 280, "today_conversations": 31, "abnormal": True},
    {"id": "dev_003", "factory_id": "fac_a", "sn": "VB202606090003", "mac_address": "A4:CF:12:11:20:03", "model": "VB-ESP32-S3-Mini", "firmware_version": "1.0.7", "batch_no": "B202605", "status": "offline", "activated_at": "2026-05-29T09:00:00Z", "last_seen_at": "2026-06-09T06:12:00Z", "current_character_id": "char_bear", "wifi_rssi": -88, "rtt_ms": 0, "today_conversations": 8, "abnormal": True},
    {"id": "dev_004", "factory_id": "fac_b", "sn": "VB202606090101", "mac_address": "A4:CF:12:11:21:01", "model": "VB-ESP32-S3", "firmware_version": "1.0.6", "batch_no": "B202606", "status": "online", "activated_at": "2026-06-03T09:00:00Z", "last_seen_at": "2026-06-09T08:59:00Z", "current_character_id": "char_dino", "wifi_rssi": -66, "rtt_ms": 92, "today_conversations": 38, "abnormal": False},
]

conversations = [
    {"id": "conv_001", "factory_id": "fac_a", "device_id": "dev_001", "character_id": "char_bear", "anonymous_session_id": "anon_8f21", "anonymous_user_label": "家庭会话 A-1028", "user_segment": "4-6 岁儿童", "started_at": "2026-06-09T08:20:00Z", "ended_at": "2026-06-09T08:22:20Z", "total_turns": 6, "success": True, "total_latency_ms": 1380, "feedback": "positive"},
    {"id": "conv_002", "factory_id": "fac_a", "device_id": "dev_002", "character_id": "char_story", "anonymous_session_id": "anon_91aa", "anonymous_user_label": "家庭会话 A-2147", "user_segment": "3-5 岁儿童", "started_at": "2026-06-09T08:30:00Z", "ended_at": "2026-06-09T08:31:10Z", "total_turns": 3, "success": False, "total_latency_ms": 4620, "feedback": "interrupted"},
    {"id": "conv_003", "factory_id": "fac_b", "device_id": "dev_004", "character_id": "char_dino", "anonymous_session_id": "anon_22c1", "anonymous_user_label": "家庭会话 B-0311", "user_segment": "6-8 岁儿童", "started_at": "2026-06-09T08:26:00Z", "ended_at": "2026-06-09T08:27:10Z", "total_turns": 4, "success": True, "total_latency_ms": 2120, "feedback": "neutral"},
]

conversation_turns = [
    {"id": "turn_001", "factory_id": "fac_a", "conversation_id": "conv_001", "device_id": "dev_001", "character_id": "char_bear", "trace_id": "trace_001", "user_asr_text": "苹果用英语怎么说", "ai_reply_text": "苹果是 apple。你可以跟我读：apple。", "intent": "英语学习", "fallback_hit": False, "safety_hit": False, "success": True, "error_code": None, "latency_total_ms": 1380, "created_at": "2026-06-09T08:20:20Z"},
    {"id": "turn_004", "factory_id": "fac_a", "conversation_id": "conv_001", "device_id": "dev_001", "character_id": "char_bear", "trace_id": "trace_004", "user_asr_text": "apple", "ai_reply_text": "很棒！apple 发音很清楚。香蕉 banana，你也想试试吗？", "intent": "跟读练习", "fallback_hit": False, "safety_hit": False, "success": True, "error_code": None, "latency_total_ms": 1210, "created_at": "2026-06-09T08:20:42Z"},
    {"id": "turn_005", "factory_id": "fac_a", "conversation_id": "conv_001", "device_id": "dev_001", "character_id": "char_bear", "trace_id": "trace_005", "user_asr_text": "香蕉怎么说", "ai_reply_text": "香蕉是 banana。我们一起读：banana。", "intent": "英语学习", "fallback_hit": False, "safety_hit": False, "success": True, "error_code": None, "latency_total_ms": 1340, "created_at": "2026-06-09T08:21:10Z"},
    {"id": "turn_002", "factory_id": "fac_a", "conversation_id": "conv_002", "device_id": "dev_002", "character_id": "char_story", "trace_id": "trace_002", "user_asr_text": "讲一个恐龙故事", "ai_reply_text": "我好像没有听清楚，可以再说一次吗？", "intent": "故事", "fallback_hit": True, "safety_hit": False, "success": False, "error_code": "ASR_LOW_CONFIDENCE", "latency_total_ms": 4620, "created_at": "2026-06-09T08:30:20Z"},
    {"id": "turn_006", "factory_id": "fac_a", "conversation_id": "conv_002", "device_id": "dev_002", "character_id": "char_story", "trace_id": "trace_006", "user_asr_text": "恐龙睡觉的故事", "ai_reply_text": "从前有一只小恐龙，它在月光下找自己的小毯子。", "intent": "睡前故事", "fallback_hit": False, "safety_hit": False, "success": True, "error_code": None, "latency_total_ms": 3560, "created_at": "2026-06-09T08:30:48Z"},
    {"id": "turn_003", "factory_id": "fac_b", "conversation_id": "conv_003", "device_id": "dev_004", "character_id": "char_dino", "trace_id": "trace_003", "user_asr_text": "霸王龙有多大", "ai_reply_text": "霸王龙很大，身长大约 12 米，像一辆小巴士那么长。", "intent": "百科问答", "fallback_hit": False, "safety_hit": False, "success": True, "error_code": None, "latency_total_ms": 2120, "created_at": "2026-06-09T08:26:20Z"},
]

latency_traces = {
    "turn_001": {"vad_ms": 120, "upload_ms": 180, "asr_ms": 260, "llm_ttft_ms": 330, "llm_total_ms": 610, "tts_first_audio_ms": 210, "tts_total_ms": 420, "playback_start_ms": 90, "e2e_first_response_ms": 1380},
    "turn_004": {"vad_ms": 90, "upload_ms": 170, "asr_ms": 230, "llm_ttft_ms": 280, "llm_total_ms": 540, "tts_first_audio_ms": 180, "tts_total_ms": 370, "playback_start_ms": 70, "e2e_first_response_ms": 1210},
    "turn_005": {"vad_ms": 110, "upload_ms": 175, "asr_ms": 250, "llm_ttft_ms": 320, "llm_total_ms": 600, "tts_first_audio_ms": 200, "tts_total_ms": 400, "playback_start_ms": 80, "e2e_first_response_ms": 1340},
    "turn_002": {"vad_ms": 260, "upload_ms": 760, "asr_ms": 1480, "llm_ttft_ms": 820, "llm_total_ms": 1240, "tts_first_audio_ms": 460, "tts_total_ms": 700, "playback_start_ms": 180, "e2e_first_response_ms": 4620},
    "turn_006": {"vad_ms": 210, "upload_ms": 610, "asr_ms": 980, "llm_ttft_ms": 690, "llm_total_ms": 1180, "tts_first_audio_ms": 390, "tts_total_ms": 680, "playback_start_ms": 150, "e2e_first_response_ms": 3560},
    "turn_003": {"vad_ms": 150, "upload_ms": 250, "asr_ms": 380, "llm_ttft_ms": 520, "llm_total_ms": 940, "tts_first_audio_ms": 330, "tts_total_ms": 580, "playback_start_ms": 110, "e2e_first_response_ms": 2120},
}

end_users = [
    {"id": "eu_001", "factory_id": "fac_a", "device_id": "dev_001", "nickname": "小明家庭", "age_range": "4-6 岁", "region": "上海", "user_segment": "儿童家庭", "bound_at": "2026-06-01T10:00:00Z", "last_active_at": "2026-06-09T08:22:00Z", "total_conversations": 128},
    {"id": "eu_002", "factory_id": "fac_a", "device_id": "dev_002", "nickname": "乐乐家", "age_range": "3-5 岁", "region": "杭州", "user_segment": "儿童家庭", "bound_at": "2026-06-02T11:00:00Z", "last_active_at": "2026-06-09T08:31:00Z", "total_conversations": 86},
    {"id": "eu_003", "factory_id": "fac_a", "device_id": "dev_003", "nickname": "豆豆家", "age_range": "5-7 岁", "region": "南京", "user_segment": "儿童家庭", "bound_at": "2026-05-29T09:30:00Z", "last_active_at": "2026-06-09T06:12:00Z", "total_conversations": 42},
    {"id": "eu_004", "factory_id": "fac_b", "device_id": "dev_004", "nickname": "天天家庭", "age_range": "6-8 岁", "region": "深圳", "user_segment": "儿童家庭", "bound_at": "2026-06-03T14:00:00Z", "last_active_at": "2026-06-09T08:27:00Z", "total_conversations": 95},
]

alerts = [
    {"id": "alert_001", "factory_id": "fac_a", "device_id": "dev_002", "alert_type": "weak_network", "severity": "high", "title": "弱网设备持续高延迟", "content": "VB202606090002 RSSI 长期低于 -75 dBm，WebSocket RTT 偏高。", "status": "open", "created_at": "2026-06-09T08:45:00Z", "resolved_at": None},
    {"id": "alert_002", "factory_id": "fac_a", "device_id": "dev_003", "alert_type": "offline", "severity": "medium", "title": "设备离线超过 2 小时", "content": "VB202606090003 最近心跳时间为 06:12。", "status": "open", "created_at": "2026-06-09T08:20:00Z", "resolved_at": None},
    {"id": "alert_003", "factory_id": "fac_b", "device_id": "dev_004", "alert_type": "fallback_rate", "severity": "low", "title": "角色兜底率升高", "content": "恐龙探险家近 24 小时兜底率高于行业中位数。", "status": "resolved", "created_at": "2026-06-08T18:20:00Z", "resolved_at": "2026-06-09T07:20:00Z"},
]
