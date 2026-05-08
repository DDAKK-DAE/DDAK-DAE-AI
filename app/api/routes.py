from fastapi import APIRouter

from app.api.challenge_routes import router as challenge_router
from app.api.chemistry_routes import router as chemistry_router
from app.api.crew_routes import router as crew_router

router = APIRouter()
router.include_router(challenge_router)
router.include_router(chemistry_router)
router.include_router(crew_router)
