import secrets
from typing import Optional

from fastapi import APIRouter, Body, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings
from app.schemas import ChallengePostRequest, ChallengePostResponse
from app.services.challenge_service import generate_challenge_post
from app.services.llm_client import LLMServiceError

router = APIRouter(prefix="/ai", tags=["AI"])

internal_api_key_header = APIKeyHeader(name="x-internal-api-key", auto_error=False)


def verify_internal_api_key(
    x_internal_api_key: Optional[str] = Security(internal_api_key_header),
) -> None:
    if not settings.INTERNAL_API_KEY:
        return
    if not secrets.compare_digest(x_internal_api_key or "", settings.INTERNAL_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal API key",
        )


@router.post(
    "/generate-description",
    response_model=ChallengePostResponse,
    dependencies=[Security(verify_internal_api_key)],
    summary="챌린지 모집글 자동 생성",
    description="Swagger 우측 상단 Authorize 버튼에 `.env`의 INTERNAL_API_KEY 값을 넣은 뒤 테스트하세요.",
    responses={
        401: {"description": "x-internal-api-key가 없거나 올바르지 않음"},
        502: {"description": "OpenAI 호출 또는 응답 검증 실패"},
    },
)
async def generate_description(
    req: ChallengePostRequest = Body(
        ...,
        examples={
            "dance": {
                "summary": "댄스 챌린지 예시",
                "value": {
                    "title": "장원영 Magnetic 챌린지",
                    "locationText": "홍대입구역 1번 출구 앞",
                    "maxParticipants": 4,
                    "category": "댄스",
                    "descriptionHint": "짧게 만나 포인트 안무를 맞추고 릴스를 촬영",
                    "mood": "설레고 친근하게",
                    "targetAudience": "초보도 환영",
                    "difficulty": "쉬움",
                },
            },
            "daily": {
                "summary": "일상 챌린지 예시",
                "value": {
                    "title": "한강 노을 산책 릴스",
                    "locationText": "여의도 한강공원",
                    "maxParticipants": 3,
                    "category": "일상",
                },
            },
        },
    ),
):
    try:
        result = await generate_challenge_post(
            title=req.title,
            location_text=req.locationText,
            max_participants=req.maxParticipants,
            category=req.category,
            description_hint=req.descriptionHint,
            mood=req.mood,
            target_audience=req.targetAudience,
            difficulty=req.difficulty,
        )
        return result
    except LLMServiceError:
        raise HTTPException(status_code=502, detail="AI description generation failed")
