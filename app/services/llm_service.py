from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

MODEL = "gpt-4o"


async def generate_challenge_post(challenge_title: str, description: str) -> str:
    """1. 챌린지 글 자동 작성"""
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "당신은 SNS 챌린지 홍보 글을 작성하는 전문가입니다. 참여를 유도하는 매력적인 글을 작성해주세요.",
            },
            {
                "role": "user",
                "content": f"챌린지 이름: {challenge_title}\n설명: {description}",
            },
        ],
    )
    return response.choices[0].message.content


async def analyze_group_chemistry(members: list[dict]) -> str:
    """2. 그룹 케미 분석"""
    member_info = "\n".join(
        [f"- {m.get('name')}: {m.get('description', '')}" for m in members]
    )
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "당신은 그룹 케미스트리를 분석하는 전문가입니다. 멤버들의 특성을 바탕으로 그룹의 시너지와 케미를 분석해주세요.",
            },
            {
                "role": "user",
                "content": f"멤버 정보:\n{member_info}",
            },
        ],
    )
    return response.choices[0].message.content


async def recommend_crew_challenge(crew_info: dict) -> str:
    """3. 크루 챌린지 추천"""
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "당신은 크루 활동 챌린지를 추천하는 전문가입니다. 크루의 특성에 맞는 챌린지를 3가지 추천해주세요.",
            },
            {
                "role": "user",
                "content": f"크루 정보: {crew_info}",
            },
        ],
    )
    return response.choices[0].message.content
