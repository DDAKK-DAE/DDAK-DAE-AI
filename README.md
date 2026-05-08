# Reels Challenge - AI Server

챌린지 글 자동 작성 / 그룹 케미 분석 / 크루 챌린지 추천을 담당하는 OpenAI API 기반 FastAPI 서버.

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
