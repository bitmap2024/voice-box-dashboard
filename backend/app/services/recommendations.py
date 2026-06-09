from typing import Any


def build_recommendations(user: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"id": "rec_latency", "type": "latency", "severity": "high", "title": "首句延迟 P95 偏高", "content": "最近 24 小时 P95 首句延迟高于行业中位数，主要瓶颈来自 LLM TTFT。建议缩短 system prompt，并降低历史上下文长度。"},
        {"id": "rec_network", "type": "device", "severity": "medium", "title": "B202606 批次弱网占比升高", "content": "弱网设备多集中在 B202606 批次，建议检查天线设计、Wi-Fi 固件和路由兼容性。"},
        {"id": "rec_prompt", "type": "prompt", "severity": "medium", "title": "故事类角色兜底率偏高", "content": "睡前故事角色启动率高，但多轮留存偏低。建议每轮结尾增加选择式引导，减少百科式长回复。"},
    ]
