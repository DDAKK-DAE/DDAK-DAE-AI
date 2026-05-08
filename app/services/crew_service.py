import json
from typing import Any, Dict, List

from app.services.llm_client import LLMServiceError, get_client

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "당신은 숏폼 릴스 챌린지 앱의 크루 챌린지 추천 큐레이터입니다.\n"
    "크루 멤버들의 카테고리 참여 빈도와 현재 트렌딩 챌린지 목록을 보고,\n"
    "이 크루에 가장 잘 어울리는 챌린지 3개를 추천하세요.\n\n"
    "조건:\n"
    "- 반드시 한국어로 reason을 작성합니다.\n"
    "- trendingChallenges 목록에 있는 챌린지만 추천합니다 (challengeId 그대로 사용).\n"
    "- 크루의 카테고리 선호도를 가장 중요한 기준으로 삼습니다.\n"
    "- reason은 1~2문장, 구체적이고 흥미롭게 작성합니다.\n"
    "- 정확히 3개를 추천합니다.\n"
    '- JSON 형식으로만 응답: {"recommendations": [{"challengeId": "...", "title": "...", "category": "...", "reason": "..."}, ...]}'
)


async def recommend_crew_challenges(
    crew_id: str,
    member_category_frequency: Dict[str, int],
    trending_challenges: List[Dict[str, Any]],
) -> Dict[str, Any]:
    payload = {
        "crewId": crew_id,
        "memberCategoryFrequency": member_category_frequency,
        "trendingChallenges": trending_challenges,
    }

    try:
        response = await get_client().chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=800,
        )
    except Exception as exc:
        raise LLMServiceError("LLM request failed") from exc

    content = response.choices[0].message.content
    if not content:
        raise LLMServiceError("empty LLM response")

    try:
        raw = json.loads(content)
    except json.JSONDecodeError as exc:
        raise LLMServiceError("LLM response was not valid JSON") from exc

    recommendations = raw.get("recommendations", [])
    if not isinstance(recommendations, list) or len(recommendations) == 0:
        raise LLMServiceError("no recommendations in LLM response")

    valid_ids = {c["id"] for c in trending_challenges}
    for item in recommendations:
        if item.get("challengeId") not in valid_ids:
            raise LLMServiceError(f"LLM returned unknown challengeId: {item.get('challengeId')}")

    return {"recommendations": recommendations[:3]}
