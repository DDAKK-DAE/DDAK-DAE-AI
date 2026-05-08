import json
from typing import Any, Dict, List

from app.schemas import ChemistryRequest
from app.services.llm_client import LLMServiceError, get_client

MODEL = "gpt-4o"

SYSTEM_PROMPT = (
    "당신은 숏폼 챌린지 그룹 케미 분석가입니다.\n"
    "챌린지 제목, 현재 멤버 이력, 신청자 이력을 분석해 케미 점수를 산정하세요.\n\n"
    "조건:\n"
    "- score: 0~100 (카테고리 일치도, 경험 수준, 분위기 종합)\n"
    "- summary: 한 줄 핵심 (40~60자, 이모지 1개)\n"
    "- comment: 멤버와 신청자를 연결한 구체적 분석 (100~200자)\n"
    "- 긍정적 톤 유지 (합류 시 시너지 강조)\n"
    "- currentMembers가 비어있으면 신청자 이력만으로 분석\n"
    '- JSON 형식으로만 응답: {"score": 87, "summary": "...", "comment": "..."}'
)


def _build_payload(req: ChemistryRequest) -> Dict[str, Any]:
    def format_member(m) -> Dict[str, Any]:
        return {
            "nickname": m.nickname,
            "bio": m.bio,
            "introMessage": m.introMessage,
            "participationHistory": [
                {"category": h.category, "title": h.title}
                for h in m.participationHistory
            ],
        }

    return {
        "challengeTitle": req.challengeTitle,
        "currentMembers": [format_member(m) for m in req.currentMembers],
        "applicant": format_member(req.applicant),
    }


async def analyze_group_chemistry(req: ChemistryRequest) -> Dict[str, Any]:
    """2. 그룹 케미 분석"""
    payload = _build_payload(req)

    try:
        response = await get_client().chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=400,
        )
    except Exception as exc:
        raise LLMServiceError("LLM request failed") from exc

    choices = getattr(response, "choices", None)
    if not choices or not getattr(choices[0], "message", None):
        raise LLMServiceError("empty LLM response")

    content = choices[0].message.content
    if not isinstance(content, str) or not content.strip():
        raise LLMServiceError("empty LLM response")

    try:
        raw = json.loads(content)
    except json.JSONDecodeError as exc:
        raise LLMServiceError("LLM response was not valid JSON") from exc

    if not isinstance(raw, dict):
        raise LLMServiceError("LLM response was not valid JSON")

    score = raw.get("score")
    summary = raw.get("summary", "")
    comment = raw.get("comment", "")

    if not isinstance(score, (int, float)) or not (0 <= score <= 100):
        raise LLMServiceError("invalid score in LLM response")
    score = int(score)
    if not isinstance(summary, str) or len(summary.strip()) < 5:
        raise LLMServiceError("summary is too short or missing")
    if not isinstance(comment, str) or len(comment.strip()) < 10:
        raise LLMServiceError("comment is too short or missing")

    return {"score": score, "summary": summary.strip(), "comment": comment.strip()}
