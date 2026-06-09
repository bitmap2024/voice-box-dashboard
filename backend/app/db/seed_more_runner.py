"""追加更多演示数据（终端用户、设备、对话、7天趋势）。用法: python -m app.db.seed_more_runner"""

from datetime import timedelta

from app.core.time import utc_now
from app.data import seed
from app.db.base import Base
from app.db.seed_runner import parse_dt
from app.db.session import SessionLocal, engine
from app.models import (
    Conversation,
    ConversationTurn,
    Device,
    DeviceTelemetry,
    EndUser,
    Factory,
    LatencyTrace,
)
from app.repositories.helpers import seed_uuid


def run_seed_more() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(EndUser).count() == 0:
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
            print("已写入终端用户绑定。")

        fac_a = next(f for f in db.query(Factory).all() if "星河" in f.name)
        fac_b = next(f for f in db.query(Factory).all() if "云朵" in f.name)

        extra_devices = [
            ("dev_005", fac_a.id, "VB202606090004", "A4:CF:12:11:20:04", "online", "char_bear", -58, 68),
            ("dev_006", fac_a.id, "VB202606090005", "A4:CF:12:11:20:05", "online", "char_story", -64, 82),
            ("dev_007", fac_a.id, "VB202606090006", "A4:CF:12:11:20:06", "warning", "char_bear", -79, 310),
            ("dev_008", fac_b.id, "VB202606090102", "A4:CF:12:11:21:02", "online", "char_dino", -61, 88),
            ("dev_009", fac_b.id, "VB202606090103", "A4:CF:12:11:21:03", "offline", "char_dino", -90, 0),
        ]
        device_map = {str(d.id): d for d in db.query(Device).all()}
        for key, fac_id, sn, mac, status, char_key, rssi, rtt in extra_devices:
            if db.get(Device, seed_uuid(key)):
                continue
            dev = Device(
                id=seed_uuid(key),
                factory_id=fac_id,
                sn=sn,
                mac_address=mac,
                model="VB-ESP32-S3",
                firmware_version="1.0.7",
                batch_no="B202606",
                status=status,
                current_character_id=seed_uuid(char_key),
                activated_at=utc_now() - timedelta(days=10),
                last_seen_at=utc_now() - timedelta(minutes=5),
            )
            db.add(dev)
            db.flush()
            device_map[str(dev.id)] = dev
            nicknames = {"dev_005": "果果家", "dev_006": "糖糖家", "dev_007": "壮壮家", "dev_008": "星星家", "dev_009": "月月家"}
            if key in nicknames and not db.query(EndUser).filter(EndUser.device_id == dev.id).first():
                db.add(
                    EndUser(
                        id=seed_uuid(f"eu_{key}"),
                        factory_id=fac_id,
                        device_id=dev.id,
                        nickname=nicknames[key],
                        age_range="4-8 岁",
                        region="华东",
                        user_segment="儿童家庭",
                        bound_at=utc_now() - timedelta(days=8),
                        last_active_at=utc_now(),
                        total_conversations=20 + len(key),
                    )
                )

        db.flush()
        all_devices = db.query(Device).all()
        now = utc_now()

        for day_offset in range(7):
            day = now - timedelta(days=6 - day_offset)
            for di, dev in enumerate(all_devices):
                for hour in [8, 12, 18]:
                    ts = day.replace(hour=hour, minute=0, second=0, microsecond=0)
                    exists = db.query(DeviceTelemetry).filter(DeviceTelemetry.device_id == dev.id, DeviceTelemetry.ts == ts).first()
                    if exists:
                        continue
                    db.add(
                        DeviceTelemetry(
                            factory_id=dev.factory_id,
                            device_id=dev.id,
                            sn=dev.sn,
                            ts=ts,
                            online=(dev.status.value if hasattr(dev.status, "value") else dev.status) != "offline",
                            wifi_rssi=-60 - (di % 5) * 4 - day_offset,
                            rtt_ms=70 + di * 10 + day_offset * 5,
                            reconnect_count=day_offset % 3,
                            upload_fail_count=0,
                            playback_fail_count=0,
                            firmware_version=dev.firmware_version,
                            free_memory=110000,
                            cpu_usage=25,
                        )
                    )

        conv_templates = [
            ("小明", "dev_001", "char_bear", "fac_a", "苹果怎么说", "Apple 是苹果。", 1280),
            ("乐乐", "dev_002", "char_story", "fac_a", "讲个故事", "从前有一只小兔子。", 2100),
            ("天天", "dev_004", "char_dino", "fac_b", "霸王龙吃什么", "霸王龙是肉食恐龙。", 1980),
            ("果果", "dev_005", "char_bear", "fac_a", "香蕉怎么说", "Banana 是香蕉。", 1150),
            ("星星", "dev_008", "char_dino", "fac_b", "翼龙会飞吗", "翼龙是会飞的。", 1760),
        ]
        for idx, (nick, dev_key, char_key, fac_key, user_text, ai_text, e2e) in enumerate(conv_templates):
            for day_offset in range(3):
                conv_id = f"conv_extra_{idx}_{day_offset}"
                if db.get(Conversation, seed_uuid(conv_id)):
                    continue
                started = now - timedelta(days=day_offset, hours=idx + 2)
                conv = Conversation(
                    id=seed_uuid(conv_id),
                    factory_id=seed_uuid(fac_key),
                    device_id=seed_uuid(dev_key),
                    character_id=seed_uuid(char_key),
                    anonymous_session_id=f"anon_extra_{idx}_{day_offset}",
                    anonymous_user_label=f"{nick}家庭会话",
                    user_segment="4-8 岁儿童",
                    started_at=started,
                    ended_at=started + timedelta(minutes=2),
                    total_turns=2,
                    success=True,
                    total_latency_ms=e2e,
                    feedback="positive",
                )
                db.add(conv)
                db.flush()
                for turn_idx in range(2):
                    turn_id = f"turn_extra_{idx}_{day_offset}_{turn_idx}"
                    trace_id = f"trace_extra_{idx}_{day_offset}_{turn_idx}"
                    latency = e2e + turn_idx * 100
                    turn = ConversationTurn(
                        id=seed_uuid(turn_id),
                        factory_id=seed_uuid(fac_key),
                        conversation_id=conv.id,
                        device_id=seed_uuid(dev_key),
                        character_id=seed_uuid(char_key),
                        trace_id=trace_id,
                        user_asr_text=user_text if turn_idx == 0 else "再说一遍",
                        ai_reply_text=ai_text if turn_idx == 0 else "好的，我再讲一次。",
                        intent="学习" if turn_idx == 0 else "重复",
                        fallback_hit=False,
                        success=True,
                        latency_total_ms=latency,
                        created_at=started + timedelta(seconds=20 * (turn_idx + 1)),
                    )
                    db.add(turn)
                    db.flush()
                    db.add(
                        LatencyTrace(
                            id=seed_uuid(f"lt_{turn_id}"),
                            factory_id=seed_uuid(fac_key),
                            device_id=seed_uuid(dev_key),
                            conversation_turn_id=turn.id,
                            trace_id=trace_id,
                            vad_ms=100,
                            upload_ms=150,
                            asr_ms=220,
                            llm_ttft_ms=300,
                            llm_total_ms=550,
                            tts_first_audio_ms=180,
                            tts_total_ms=350,
                            playback_start_ms=80,
                            e2e_first_response_ms=latency,
                            created_at=turn.created_at,
                        )
                    )

        if db.query(Conversation).count() < 150:
            user_phrases = [
                ("讲个故事", "从前有一只小兔子。"),
                ("苹果怎么说", "Apple 是苹果。"),
                ("今天天气怎么样", "今天阳光明媚。"),
                ("恐龙吃什么", "霸王龙是肉食恐龙。"),
                ("再说一遍", "好的，我再讲一次。"),
                ("你好", "你好呀，很高兴见到你。"),
                ("唱首歌", "啦啦啦，我们一起唱。"),
                ("几点了", "现在是下午三点。"),
            ]
            all_devices = db.query(Device).all()
            bulk_target = 220
            bulk_idx = 0
            while db.query(Conversation).count() < bulk_target and bulk_idx < 500:
                dev = all_devices[bulk_idx % len(all_devices)]
                phrase = user_phrases[bulk_idx % len(user_phrases)]
                conv_id = f"conv_bulk_{bulk_idx}"
                if db.get(Conversation, seed_uuid(conv_id)):
                    bulk_idx += 1
                    continue
                started = now - timedelta(days=bulk_idx % 30, hours=bulk_idx % 12, minutes=(bulk_idx * 7) % 60)
                e2e = 900 + (bulk_idx % 15) * 120
                success = bulk_idx % 17 != 0
                conv = Conversation(
                    id=seed_uuid(conv_id),
                    factory_id=dev.factory_id,
                    device_id=dev.id,
                    character_id=dev.current_character_id,
                    anonymous_session_id=f"anon_bulk_{bulk_idx}",
                    anonymous_user_label=f"家庭会话 #{bulk_idx + 1}",
                    user_segment="4-8 岁儿童" if bulk_idx % 2 == 0 else "亲子互动",
                    started_at=started,
                    ended_at=started + timedelta(minutes=3),
                    total_turns=2,
                    success=success,
                    total_latency_ms=e2e * 2,
                    feedback="positive" if success else "negative",
                )
                db.add(conv)
                db.flush()
                for turn_idx in range(2):
                    turn_id = f"turn_bulk_{bulk_idx}_{turn_idx}"
                    trace_id = f"trace_bulk_{bulk_idx}_{turn_idx}"
                    latency = e2e + turn_idx * 80
                    turn = ConversationTurn(
                        id=seed_uuid(turn_id),
                        factory_id=dev.factory_id,
                        conversation_id=conv.id,
                        device_id=dev.id,
                        character_id=dev.current_character_id,
                        trace_id=trace_id,
                        user_asr_text=phrase[0] if turn_idx == 0 else "再说一遍",
                        ai_reply_text=phrase[1] if turn_idx == 0 else "好的，我再讲一次。",
                        intent="学习" if turn_idx == 0 else "重复",
                        fallback_hit=bulk_idx % 23 == 0,
                        safety_hit=False,
                        success=success,
                        latency_total_ms=latency,
                        created_at=started + timedelta(seconds=15 * (turn_idx + 1)),
                    )
                    db.add(turn)
                    db.flush()
                    db.add(
                        LatencyTrace(
                            id=seed_uuid(f"lt_{turn_id}"),
                            factory_id=dev.factory_id,
                            device_id=dev.id,
                            conversation_turn_id=turn.id,
                            trace_id=trace_id,
                            vad_ms=90 + turn_idx * 10,
                            upload_ms=140,
                            asr_ms=210,
                            llm_ttft_ms=280,
                            llm_total_ms=520,
                            tts_first_audio_ms=170,
                            tts_total_ms=340,
                            playback_start_ms=75,
                            e2e_first_response_ms=latency,
                            created_at=turn.created_at,
                        )
                    )
                bulk_idx += 1
            print(f"已批量生成对话至 {db.query(Conversation).count()} 条。")

        db.commit()
        print(f"追加完成：设备 {db.query(Device).count()} 台，终端用户 {db.query(EndUser).count()} 人，对话 {db.query(Conversation).count()} 条。")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed_more()
