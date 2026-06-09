"""将内存种子数据写入 PostgreSQL。用法: python -m app.db.seed_runner"""

from datetime import datetime, timedelta

from app.core.security import hash_password
from app.core.time import utc_now
from app.data import seed
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import (
    AICharacter,
    AdminUser,
    Alert,
    Conversation,
    ConversationTurn,
    Device,
    DeviceTelemetry,
    EndUser,
    Factory,
    LatencyTrace,
    Permission,
    PromptVersion,
    Role,
    RolePermission,
)
from app.repositories.helpers import seed_uuid


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def run_seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Factory).count() > 0:
            print("数据库已有数据，跳过 seed。")
            return

        perm_defs = [
            {"code": "*", "name": "全部权限", "module": "system"},
            {"code": "dashboard:read", "name": "看板读取", "module": "dashboard"},
            {"code": "device:*", "name": "设备管理", "module": "device"},
            {"code": "device:read", "name": "设备读取", "module": "device"},
            {"code": "character:*", "name": "角色管理", "module": "character"},
            {"code": "character:read", "name": "角色读取", "module": "character"},
            {"code": "conversation:read", "name": "对话读取", "module": "conversation"},
            {"code": "conversation:trace", "name": "链路追踪", "module": "conversation"},
            {"code": "user:*", "name": "用户管理", "module": "user"},
            {"code": "industry:read", "name": "行业分析", "module": "industry"},
            {"code": "alert:*", "name": "告警管理", "module": "alert"},
        ]
        permissions: dict[str, Permission] = {}
        for item in perm_defs:
            perm = Permission(id=seed_uuid(f"perm_{item['code']}"), code=item["code"], name=item["name"], module=item["module"])
            db.add(perm)
            permissions[item["code"]] = perm
        db.flush()

        role_map: dict[str, Role] = {}
        for item in seed.roles:
            role = Role(
                id=seed_uuid(item["id"]),
                code=item["code"],
                name=item["name"],
                is_system=True,
            )
            db.add(role)
            role_map[item["code"]] = role
        db.flush()

        for item in seed.roles:
            role = role_map[item["code"]]
            for perm_code in item["permissions"]:
                if perm_code == "*":
                    for perm in permissions.values():
                        db.add(RolePermission(role_id=role.id, permission_id=perm.id))
                elif perm_code.endswith(":*"):
                    prefix = perm_code[:-2]
                    for code, perm in permissions.items():
                        if code.startswith(prefix):
                            db.add(RolePermission(role_id=role.id, permission_id=perm.id))
                elif perm_code in permissions:
                    db.add(RolePermission(role_id=role.id, permission_id=permissions[perm_code].id))

        factory_map: dict[str, Factory] = {}
        for item in seed.factories:
            fac = Factory(
                id=seed_uuid(item["id"]),
                name=item["name"],
                industry=item["industry"],
                status=item["status"],
                plan_type=item["plan_type"],
                device_quota=item["device_quota"],
                created_at=parse_dt(item["created_at"]),
            )
            db.add(fac)
            factory_map[item["id"]] = fac
        db.flush()

        user_map: dict[str, AdminUser] = {}
        for item in seed.admin_users:
            user = AdminUser(
                id=seed_uuid(item["id"]),
                factory_id=seed_uuid(item["factory_id"]) if item["factory_id"] else None,
                role_id=role_map[item["role_code"]].id,
                name=item["name"],
                email=item["email"],
                phone=item["phone"],
                password_hash=hash_password(item["password"]),
                status=item["status"],
                last_login_at=parse_dt(item["last_login_at"]),
            )
            db.add(user)
            user_map[item["id"]] = user
        db.flush()

        char_map: dict[str, AICharacter] = {}
        for item in seed.characters:
            char = AICharacter(
                id=seed_uuid(item["id"]),
                factory_id=seed_uuid(item["factory_id"]),
                name=item["name"],
                scene_type=item["scene_type"],
                age_range=item["age_range"],
                tone_style=item["tone_style"],
                description=item["description"],
                status=item["status"],
            )
            db.add(char)
            char_map[item["id"]] = char
        db.flush()

        pv_map: dict[str, PromptVersion] = {}
        for item in seed.prompt_versions:
            creator = next((u for u in seed.admin_users if u["name"] == item["created_by"]), None)
            pv = PromptVersion(
                id=seed_uuid(item["id"]),
                factory_id=seed_uuid(item["factory_id"]),
                character_id=seed_uuid(item["character_id"]),
                version=item["version"],
                system_prompt=item["system_prompt"],
                structured_config=item["structured_config"],
                change_note=item["change_note"],
                status=item["status"],
                created_by=seed_uuid(creator["id"]) if creator else None,
                created_at=parse_dt(item["created_at"]),
                published_at=parse_dt(item.get("published_at")),
            )
            db.add(pv)
            pv_map[item["id"]] = pv
        db.flush()

        for item in seed.characters:
            char = char_map[item["id"]]
            if item.get("current_prompt_version_id"):
                char.current_prompt_version_id = seed_uuid(item["current_prompt_version_id"])

        device_map: dict[str, Device] = {}
        for item in seed.devices:
            dev = Device(
                id=seed_uuid(item["id"]),
                factory_id=seed_uuid(item["factory_id"]),
                sn=item["sn"],
                mac_address=item["mac_address"],
                model=item["model"],
                firmware_version=item["firmware_version"],
                batch_no=item["batch_no"],
                status=item["status"],
                current_character_id=seed_uuid(item["current_character_id"]) if item.get("current_character_id") else None,
                activated_at=parse_dt(item.get("activated_at")),
                last_seen_at=parse_dt(item.get("last_seen_at")),
            )
            db.add(dev)
            device_map[item["id"]] = dev
        db.flush()

        for item in seed.conversations:
            conv = Conversation(
                id=seed_uuid(item["id"]),
                factory_id=seed_uuid(item["factory_id"]),
                device_id=seed_uuid(item["device_id"]),
                character_id=seed_uuid(item["character_id"]) if item.get("character_id") else None,
                anonymous_session_id=item.get("anonymous_session_id"),
                anonymous_user_label=item.get("anonymous_user_label"),
                user_segment=item.get("user_segment"),
                started_at=parse_dt(item["started_at"]),
                ended_at=parse_dt(item.get("ended_at")),
                total_turns=item["total_turns"],
                success=item["success"],
                total_latency_ms=item.get("total_latency_ms"),
                feedback=item.get("feedback"),
            )
            db.add(conv)
        db.flush()

        turn_map: dict[str, ConversationTurn] = {}
        for item in seed.conversation_turns:
            turn = ConversationTurn(
                id=seed_uuid(item["id"]),
                factory_id=seed_uuid(item["factory_id"]),
                conversation_id=seed_uuid(item["conversation_id"]),
                device_id=seed_uuid(item["device_id"]),
                character_id=seed_uuid(item["character_id"]) if item.get("character_id") else None,
                trace_id=item["trace_id"],
                user_asr_text=item.get("user_asr_text"),
                ai_reply_text=item.get("ai_reply_text"),
                intent=item.get("intent"),
                fallback_hit=item.get("fallback_hit", False),
                safety_hit=item.get("safety_hit", False),
                success=item.get("success", True),
                error_code=item.get("error_code"),
                latency_total_ms=item.get("latency_total_ms"),
                created_at=parse_dt(item["created_at"]),
            )
            db.add(turn)
            turn_map[item["id"]] = turn
        db.flush()

        for turn_id, trace_data in seed.latency_traces.items():
            turn = turn_map[turn_id]
            trace = LatencyTrace(
                id=seed_uuid(f"lt_{turn_id}"),
                factory_id=turn.factory_id,
                device_id=turn.device_id,
                conversation_turn_id=turn.id,
                trace_id=turn.trace_id,
                **trace_data,
            )
            db.add(trace)

        for item in seed.end_users:
            db.add(
                EndUser(
                    id=seed_uuid(item["id"]),
                    factory_id=seed_uuid(item["factory_id"]),
                    device_id=seed_uuid(item["device_id"]),
                    nickname=item["nickname"],
                    age_range=item.get("age_range"),
                    region=item.get("region"),
                    user_segment=item.get("user_segment"),
                    bound_at=parse_dt(item.get("bound_at")),
                    last_active_at=parse_dt(item.get("last_active_at")),
                    total_conversations=item.get("total_conversations", 0),
                )
            )

        for item in seed.alerts:
            alert = Alert(
                id=seed_uuid(item["id"]),
                factory_id=seed_uuid(item["factory_id"]),
                device_id=seed_uuid(item["device_id"]) if item.get("device_id") else None,
                alert_type=item["alert_type"],
                severity=item["severity"],
                title=item["title"],
                content=item["content"],
                status=item["status"],
                created_at=parse_dt(item["created_at"]),
                resolved_at=parse_dt(item.get("resolved_at")),
            )
            db.add(alert)

        now = utc_now()
        for dev_id, dev in device_map.items():
            seed_dev = next(d for d in seed.devices if d["id"] == dev_id)
            for index in range(24):
                ts = now - timedelta(hours=23 - index)
                db.add(
                    DeviceTelemetry(
                        factory_id=dev.factory_id,
                        device_id=dev.id,
                        sn=dev.sn,
                        ts=ts,
                        online=seed_dev["status"] != "offline" if index > 2 else seed_dev["status"] == "online",
                        wifi_rssi=seed_dev["wifi_rssi"] + ((index % 5) - 2) * 2,
                        rtt_ms=max(seed_dev["rtt_ms"], 60) + (index % 6) * 15,
                        reconnect_count=index % 4,
                        upload_fail_count=1 if index % 9 == 0 else 0,
                        playback_fail_count=1 if index % 13 == 0 else 0,
                        firmware_version=dev.firmware_version,
                        free_memory=120000 - index * 380,
                        cpu_usage=24 + index % 30,
                    )
                )

        db.commit()
        print("Seed 完成。")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
