# 数据库设计

本系统是多租户 AI 语音硬件 ToB SaaS 控制台。数据库按三类数据设计：

1. **业务主数据**：工厂、后台用户、权限、设备、AI 角色、Prompt 版本。
2. **高频明细数据**：设备遥测、对话 turn、链路 latency trace、告警事件。
3. **分析聚合数据**：工厂日指标、行业匿名 benchmark、规则型优化建议。

MVP 建议先使用 PostgreSQL。数据量上来后，把 `device_telemetry`、`latency_traces`、`conversation_turns` 的分析查询副本同步到 ClickHouse。

## 多租户原则

- 除平台级表外，所有业务表必须包含 `factory_id`。
- 工厂后台用户所有查询必须自动追加 `factory_id = 当前用户.factory_id`。
- 平台管理员可以跨工厂查询，但敏感行业分析仍只能使用匿名聚合结果。
- `sn` 全局唯一，设备归属以 `devices.factory_id` 为准。
- 对话记录不做消费者用户体系，只保留 `anonymous_session_id`。

## PostgreSQL 表分组

### 租户与权限

- `factories`：工厂租户。
- `admin_users`：后台用户。
- `roles`：角色。
- `permissions`：权限点。
- `role_permissions`：角色权限关系。
- `audit_logs`：登录、配置、发布、绑定等操作审计。

### 设备运维

- `devices`：ESP32 设备主数据。
- `device_bindings`：SN 绑定历史。
- `device_telemetry`：设备时序遥测，建议按月分区。
- `device_events`：离线、重连、升级、播放失败等事件。
- `alerts`：告警。

### 语音对话运营

- `ai_characters`：AI 角色。
- `prompt_versions`：Prompt 版本。
- `conversations`：一次会话。
- `conversation_turns`：单轮对话。
- `latency_traces`：ASR/LLM/TTS/VAD/播放链路耗时。
- `badcases`：人工或规则标记的问题样本。

### 行业分析

- `factory_daily_metrics`：工厂每日聚合指标。
- `industry_daily_benchmarks`：行业匿名 benchmark。
- `recommendations`：规则或 AI 生成的优化建议。

## 核心索引策略

- 多租户列表查询：`(factory_id, created_at desc)`。
- 设备查询：`sn unique`、`(factory_id, status)`、`(factory_id, firmware_version)`。
- 对话查询：`(factory_id, started_at desc)`、`(factory_id, device_id, started_at desc)`。
- 时序查询：`(factory_id, device_id, ts desc)`。
- Trace 查询：`trace_id unique`、`conversation_turn_id unique`。

## 数据生命周期

- 业务主数据：长期保存。
- 设备遥测原始点：默认保存 90 天，之后只保留小时/日聚合。
- 对话文本：按客户合同配置，默认 180 天。
- 原始音频：对象存储，默认 30-90 天，数据库只存 URL 和元数据。
- 行业 benchmark：长期保存，但只保存匿名聚合，不保存可反推单工厂的信息。

## 后续接入 SQLAlchemy

FastAPI 当前先用 seed 数据跑通接口。落库时建议：

- `backend/app/db/session.py`：数据库连接。
- `backend/app/models/`：SQLAlchemy ORM。
- `backend/app/repositories/`：按模块封装查询。
- `backend/alembic/`：迁移脚本。
- API 层保持现有 `routers` 不变，只替换数据访问实现。
