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


# ── 엔드포인트 2: 그룹 케미 분석 ──────────────────────────────

class ParticipationHistory(BaseModel):
    category: str
    title: str


class MemberProfile(BaseModel):
    nickname: str
    bio: Optional[str] = None
    introMessage: Optional[str] = None
    participationHistory: List[ParticipationHistory] = []


class ChemistryRequest(BaseModel):
    challengeTitle: str
    currentMembers: List[MemberProfile]
    applicant: MemberProfile

    model_config = {
        "json_schema_extra": {
            "example": {
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
            }
        }
    }


class ChemistryResponse(BaseModel):
    score: int
    summary: str
    comment: str
