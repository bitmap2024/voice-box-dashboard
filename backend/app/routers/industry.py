from typing import Any

from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.services.recommendations import build_recommendations

router = APIRouter()


@router.get("/benchmarks")
def benchmarks(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    return {
        "industry": "AI 玩具",
        "sample_factory_count": 23,
        "metrics": [
            {"metric": "在线率", "factory_value": 84.2, "industry_median": 88.0, "top25": 94.0, "conclusion": "略低"},
            {"metric": "日活设备率", "factory_value": 18.0, "industry_median": 24.0, "top25": 36.0, "conclusion": "偏低"},
            {"metric": "平均对话轮数", "factory_value": 3.2, "industry_median": 4.8, "top25": 7.1, "conclusion": "偏低"},
            {"metric": "P95 首句延迟", "factory_value": 3.5, "industry_median": 2.6, "top25": 1.8, "conclusion": "偏高"},
            {"metric": "兜底回复率", "factory_value": 12.0, "industry_median": 7.0, "top25": 4.0, "conclusion": "偏高"},
        ],
        "hot_roles": [
            {"name": "睡前故事", "value": 34},
            {"name": "英语陪练", "value": 28},
            {"name": "百科问答", "value": 19},
            {"name": "情绪陪伴", "value": 11},
        ],
    }


@router.get("/comparison")
def comparison(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    return benchmarks(user)


@router.get("/recommendations")
def recommendations(user: dict[str, Any] = Depends(get_current_user)) -> list[dict[str, Any]]:
    return build_recommendations(user)
