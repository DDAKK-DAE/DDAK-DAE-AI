from fastapi import APIRouter, Body, HTTPException, Security

from app.api.challenge_routes import verify_internal_api_key
from app.schemas import CrewRecommendationRequest, CrewRecommendationResponse
from app.services.crew_service import recommend_crew_challenges
from app.services.llm_client import LLMServiceError

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post(
    "/crew-recommendation",
    response_model=CrewRecommendationResponse,
    dependencies=[Security(verify_internal_api_key)],
    summary="크루 챌린지 추천",
    description="크루 멤버들의 카테고리 선호도와 트렌딩 챌린지를 기반으로 다음 챌린지 3개를 추천합니다.",
    responses={
        401: {"description": "x-internal-api-key가 없거나 올바르지 않음"},
        502: {"description": "OpenAI 호출 또는 응답 검증 실패"},
    },
)
async def crew_recommendation(
    req: CrewRecommendationRequest = Body(...),
):
    try:
        result = await recommend_crew_challenges(
            crew_id=req.crewId,
            member_category_frequency=req.memberCategoryFrequency,
            trending_challenges=[c.model_dump() for c in req.trendingChallenges],
        )
        return result
    except LLMServiceError:
        raise HTTPException(status_code=502, detail="AI crew recommendation failed")