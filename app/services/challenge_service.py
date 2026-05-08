import json
import re
from typing import Any, Dict, List, Optional

from app.services.llm_client import LLMServiceError, get_client

MODEL = "gpt-4o"
TARGET_HASHTAG_COUNT = 5

CATEGORY_GUIDES = {
    "댄스": "안무, 포인트 동작, 싱크, 릴스 촬영 분위기를 살린다.",
    "일상": "가볍게 모이는 동네 감성, 기록하고 싶은 순간, 편안한 참여감을 살린다.",
    "스포츠": "에너지, 팀워크, 가벼운 운동, 인증샷/숏폼으로 남기는 성취감을 살린다.",
    "푸드": "맛집, 메뉴, 같이 먹고 찍는 즐거움, 짧은 리뷰 릴스 분위기를 살린다.",
    "기타": "챌린지 주제의 재미와 함께 모이는 이유를 구체적으로 살린다.",
}


def _normalize_hashtags(values: Any, payload: Dict[str, Any]) -> List[str]:
    fallbacks = [
        re.sub(r"\s+", "", payload["title"]),
        f"{payload['category']}챌린지",
        re.sub(r"\s+", "", payload["locationText"]),
        "릴스",
        "같이찍어요",
        "동네챌린지",
    ]

    raw_values = values if isinstance(values, list) else re.split(r"[\s,]+", values or "")
    normalized, seen = [], set()

    for raw in raw_values + fallbacks:
        if not isinstance(raw, str):
            continue
        tag = "#" + re.sub(r"[^\w가-힣]", "", raw.strip().lstrip("#").replace(" ", ""))
        if len(tag) <= 1 or tag.lower() in seen:
            continue
        seen.add(tag.lower())
        normalized.append(tag[:24])
        if len(normalized) == TARGET_HASHTAG_COUNT:
            break

    if len(normalized) != TARGET_HASHTAG_COUNT:
        raise LLMServiceError("not enough valid hashtags")
    return normalized


async def generate_challenge_post(
    title: str,
    location_text: str,
    max_participants: int,
    category: str,
    description_hint: Optional[str] = None,
    mood: Optional[str] = None,
    target_audience: Optional[str] = None,
    difficulty: Optional[str] = None,
) -> Dict[str, Any]:
    """1. 챌린지 글 자동 작성"""
    payload = {
        "title": title,
        "locationText": location_text,
        "maxParticipants": max_participants,
        "category": category,
        "descriptionHint": description_hint,
        "mood": mood,
        "targetAudience": target_audience,
        "difficulty": difficulty,
    }

    system_prompt = (
        "당신은 숏폼 챌린지 모임 앱의 모집 글 작성 도우미입니다.\n"
        "MZ 감성의 친근하고 설레는 모집 글과 해시태그를 생성하세요.\n\n"
        "조건:\n"
        "- 반드시 한국어로 작성합니다.\n"
        "- 이모지 1~2개 포함, 150~250자 분량\n"
        "- 챌린지명, 장소, 모집 인원을 자연스럽게 포함\n"
        "- 해시태그 정확히 5개, 모두 #으로 시작, 공백 없음\n"
        f"- 카테고리 가이드: {CATEGORY_GUIDES.get(category, CATEGORY_GUIDES['기타'])}\n\n"
        '- JSON 형식으로만 응답: {"description": "...", "hashtags": ["#...", ...]}'
    )

    response = await get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
        max_tokens=600,
    )

    content = response.choices[0].message.content
    if not content:
        raise LLMServiceError("empty LLM response")

    try:
        raw = json.loads(content)
    except json.JSONDecodeError as exc:
        raise LLMServiceError("LLM response was not valid JSON") from exc

    description = raw.get("description", "")
    if not isinstance(description, str) or len(description.strip()) < 40:
        raise LLMServiceError("description is too short or missing")

    return {
        "description": description.strip(),
        "hashtags": _normalize_hashtags(raw.get("hashtags"), payload),
    }
