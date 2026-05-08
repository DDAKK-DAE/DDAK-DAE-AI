import secrets
from typing import Optional

from fastapi import APIRouter, Body, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings
from app.schemas import ChemistryRequest, ChemistryResponse
from app.services.chemistry_service import analyze_group_chemistry
from app.services.llm_client import LLMServiceError

router = APIRouter(prefix="/ai", tags=["AI"])

internal_api_key_header = APIKeyHeader(name="x-internal-api-key", auto_error=False)


def verify_internal_api_key(
    x_internal_api_key: Optional[str] = Security(internal_api_key_header),
) -> None:
    if not settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="INTERNAL_API_KEY is not configured",
        )
    if not secrets.compare_digest(x_internal_api_key or "", settings.INTERNAL_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal API key",
        )


@router.post(
    "/chemistry",
    response_model=ChemistryResponse,
    dependencies=[Security(verify_internal_api_key)],
    summary="그룹 케미 분석",
    description="현재 확정 멤버와 신청자의 이력을 분석해 케미 점수와 코멘트를 반환합니다.",
    responses={
        401: {"description": "x-internal-api-key가 없거나 올바르지 않음"},
        502: {"description": "OpenAI 호출 또는 응답 검증 실패"},
    },
)
async def chemistry(
    req: ChemistryRequest = Body(
        ...,
        examples={
            "default": {
                "summary": "케미 분석 예시",
                "value": {
                    "challengeTitle": "장원영 Magnetic 챌린지",
                    "currentMembers": [
                        {
                            "nickname": "alice",
                            "bio": "댄스 유튜버, 걸그룹 안무 전문",
                            "participationHistory": [
                                {"category": "댄스", "title": "뉴진스 Hype Boy 챌린지"},
                                {"category": "댄스", "title": "아이브 LOVE DIVE 챌린지"},
                            ],
                        }
                    ],
                    "applicant": {
                        "nickname": "diana",
                        "bio": "취미로 방송댄스 배우는 중 🎵",
                        "introMessage": "평소에 장원영 팬이에요! 같이 찍고 싶어요 🙏",
                        "participationHistory": [
                            {"category": "댄스", "title": "에스파 Spicy 챌린지"}
                        ],
                    },
                },
            }
        },
    ),
):
    try:
        return await analyze_group_chemistry(req)
    except LLMServiceError:
        raise HTTPException(status_code=502, detail="AI chemistry analysis failed")
