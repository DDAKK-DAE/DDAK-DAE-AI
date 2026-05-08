from typing import List, Optional

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
