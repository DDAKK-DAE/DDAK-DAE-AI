from fastapi import APIRouter

from app.api.challenge_routes import router as challenge_router

router = APIRouter()
router.include_router(challenge_router)

# 팀원 작업 완료 후 아래 주석 해제
# from app.api.crew_routes import router as crew_router
# router.include_router(crew_router)
