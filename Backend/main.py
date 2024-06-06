from fastapi import FastAPI, HTTPException, Query, Form
from pydantic import BaseModel
import openai
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# 설정된 루트 경로와 문서 경로를 로깅하기 위한 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

root_path = "/api/v1"

app = FastAPI(
    root_path=root_path,
    docs_url=f"{root_path}/docs",  # Swagger UI 경로
    redoc_url=f"{root_path}/redoc",  # ReDoc 경로
    openapi_url=f"{root_path}/openapi.json"  # OpenAPI 스키마 경로
)

# 앱이 시작될 때 로그 메시지를 출력합니다.
@app.on_event("startup")
async def startup_event():
    logger.info(f"Root path is set to: {root_path}")
    logger.info(f"Swagger UI is available at: {root_path}/docs")
    logger.info(f"ReDoc is available at: {root_path}/redoc")
    logger.info(f"OpenAPI schema is available at: {root_path}/openapi.json")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 프론트엔드 도메인을 추가
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 단어 생성 모델 호출 함수
def generate_word(category: str, difficulty: str) -> str:
    try:
        prompt = f"단어를 추측해 봐. 단어에 대해서 두 가지 정보를 알려줄 거야. 첫째로 category는 단어의 범주이다. 영화제목, 동식물, 노래제목, 여행지, 음식메뉴, 사물 중에 하나이다. 둘째로 difficulty는 쉬운, 어려운 중에 하나이다. 쉬운 단어는 한국 사람들이 자주 사용하는 단어이고 어려운 단어는 한국 사람들이 잘 알지 못하는 단어이다. 이제 정보를 알려줄게. 단어의 category는 {category}이고 단어의 difficulty는 {difficulty}야. 이 단어는 무엇일까? 정확히 단어만 출력해."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        result = response.choices[0].message['content']
        return result
    except openai.OpenAIError as e:
        logger.error(f"Error generating word: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ChatGPT API 호출 함수
def get_chatgpt_response(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return response.choices[0].message['content'].strip()
    except openai.OpenAIError as e:
        logger.error(f"Error getting ChatGPT response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 게임 시작 엔드포인트 정의
@app.get("/start_game")
async def start_game(category: str = Query(...), difficulty: str = Query(...)):
    logger.debug(f"start_game called with category: {category}, difficulty: {difficulty}")
    word = generate_word(category, difficulty)
    return {"message": "Game started", "category": category, "difficulty": difficulty, "word": word}

# 질문 엔드포인트 정의
@app.get("/ask", response_model=dict)
async def ask_question(question: str = Query(...), word: str = Query(...)):
    try:
        logger.debug(f"ask_question called with question: {question}, word: {word}")
        prompt = f"'{word}'에 대한 질문: '{question}'. 예 아니오로만 대답해줘."
        answer = get_chatgpt_response(prompt)
        return {"word": word, "question": question, "answer": answer }
    except HTTPException as e:
        logger.error(f"HTTPException in ask_question: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Exception in ask_question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 정답 엔드포인트 정의
@app.get("/guess", response_model=dict)
async def guess_answer(guess: str = Query(...), word: str = Query(...), category: str = Query(...)):
    try:
        logger.debug(f"guess_answer called with guess: {guess}, word: {word}, category: {category}")
        prompt = f"{guess}와 {word}가 동일한 {category}라고 생각해? 정확히 true 또는 false 둘 중 하나만 반환해."
        answer = get_chatgpt_response(prompt)
        return { "answer": answer }
    except HTTPException as e:
        logger.error(f"HTTPException in guess_answer: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Exception in guess_answer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# FastAPI 서버를 실행하는 부분
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
