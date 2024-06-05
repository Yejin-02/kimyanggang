from fastapi import FastAPI, HTTPException, Query, Form
from pydantic import BaseModel
import openai
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
        prompt = f"나는 스무고개 게임의 딜러이다. 스무고개 게임의 딜러는 단어를 고르는 역할을 한다. 스무고개 게임의 플레이어는 단어에 대한 질문을 한다. 딜러는 질문에 예/아니오로 답할 수 있다. 딜러는 플레이어가 원하는 category와 difficulty의 단어를 골라야 한다. category는 영화제목, 동식물, 노래제목, 장소, 음식 중에 하나이다. 딜러가 고르는 단어는 category의 예시 단어이고, 구체적인 실존 단어여야 한다. difficulty는 쉬운, 어려운 중에 하나이다. 쉬운 단어는 사람들이 자주 사용하는 단어이고 어려운 단어는 사람들이 잘 알지 못하는 단어이다. category가 '{category}'인 단어 중 '{difficulty}' 예시 단어를 골라야 한다. 단 하나의 예시 단어만 단답형으로 출력해."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        return response.choices[0].message['content'].strip()
    except openai.OpenAIError as e:
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
        raise HTTPException(status_code=500, detail=str(e))

# 게임 시작 엔드포인트 정의
@app.get("/start_game")
async def start_game(category: str = Query(...), difficulty: str = Query(...)):
    word = generate_word(category, difficulty)
    return {"message": "Game started", "category": category, "difficulty": difficulty, "word": word}

# 질문 엔드포인트 정의
@app.get("/ask", response_model=dict)
async def ask_question(question: str = Query(...), word: str = Query(...)):
    try:
        prompt = f"'{word}'에 대한 질문: '{question}'. 예 아니오로만 대답해줘."
        answer = get_chatgpt_response(prompt)
        return {"word": word, "question": question, "answer": answer }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# FastAPI 서버를 실행하는 부분
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
