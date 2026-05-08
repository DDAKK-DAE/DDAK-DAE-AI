from typing import Dict, List, Optional

from pydantic import BaseModel, Field, conint, constr


class ChallengePostRequest(BaseModel):
    title: constr(strip_whitespace=True, min_length=1, max_length=100)
    locationText: constr(strip_whitespace=True, min_length=1, max_length=100)
    maxParticipants: conint(ge=2, le=6)
    category: constr(strip_whitespace=True, min_length=1, max_length=20)
    descriptionHint: Optional[constr(strip_whitespace=True, max_length=300)] = None
    mood: Optional[constr(strip_whitespace=True, max_length=50)] = None
    targetAudience: Optional[constr(strip_whitespace=True, max_length=80)] = None
    difficulty: Optional[constr(strip_whitespace=True, max_length=30)] = None


class ChallengePostResponse(BaseModel):
    description: str
    hashtags: List[str] = Field(..., min_items=5, max_items=5)


# ── 크루 챌린지 추천 ────────────────────────────────────────

class TrendingChallenge(BaseModel):
    id: str
    title: str
    category: str
    locationText: str
    hashtags: Optional[List[str]] = None


class CrewRecommendationRequest(BaseModel):
    crewId: str
    memberCategoryFrequency: Dict[str, int]
    trendingChallenges: List[TrendingChallenge]


class RecommendationItem(BaseModel):
    challengeId: str
    title: str
    category: str
    reason: str


class CrewRecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem] = Field(..., min_items=1, max_items=3)
