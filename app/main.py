from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Reels Challenge - AI Server",
    description=(
        "Spring Boot 백엔드가 내부 호출하는 AI 서버입니다. "
        "Swagger 테스트 시 Authorize 버튼에 x-internal-api-key 값을 입력하세요."
    ),
    version="0.1.0",
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
