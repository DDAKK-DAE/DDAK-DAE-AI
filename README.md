# Reels Challenge - AI Server

챌린지 글 자동 작성 / 그룹 케미 분석 / 크루 챌린지 추천을 담당하는 OpenAI API 기반 FastAPI 서버.
프론트엔드가 직접 호출하지 않고 Spring Boot 백엔드가 내부 API로 호출합니다.

## 로컬 실행

```bash
py -3.10 -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
cp .env.example .env         # API 키 입력 후 저장

uvicorn app.main:app --reload --port 8000
```

## 도커 실행

```bash
docker build -t reels-challenge-ai .
docker run -p 8000:8000 --env-file .env reels-challenge-ai
```

헬스체크: `GET http://localhost:8000/health`

## Spring Boot 연동

AI API는 Spring Boot에서만 호출합니다. 모든 `/ai/*` 요청에는 `.env`의
`INTERNAL_API_KEY`와 같은 값을 `x-internal-api-key` 헤더로 전달해야 합니다.

```bash
curl -X POST http://localhost:8000/ai/generate-description \
  -H "content-type: application/json" \
  -H "x-internal-api-key: change-this-shared-secret" \
  -d '{
    "title": "장원영 Magnetic 챌린지",
    "locationText": "홍대입구역 1번 출구 앞",
    "maxParticipants": 4,
    "category": "댄스",
    "mood": "설레고 친근하게",
    "targetAudience": "초보도 환영"
  }'
```
