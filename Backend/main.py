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
        prompt = f"단어를 추측해 봐. 단어에 대해서 두 가지 정보를 알려줄 거야. 첫째로 category는 단어의 범주이다. 영화제목, 동식물, 노래제목, 여행지, 음식메뉴, 사물 중에 하나이다. 둘째로 difficulty는 쉬운, 어려운 중에 하나이다. 쉬운 단어는 한국 사람들이 자주 사용하는 단어이고 어려운 단어는 한국 사람들이 잘 알지 못하는 단어이다. 이제 정보를 알려줄게. 단어의 category는 {category}이고 단어의 difficulty는 {difficulty}야. 이 단어는 무엇일까? 정확히 단어만 출력해."
#        prompt = f"category는 단어의 범주로, 영화 제목, 동식물, 지역 이름, 음식 메뉴, 사물 중에 하나이다. difficulty는 단어의 난이도로, 쉬운(한국 사람들이 잘 아는), 어려운(한국 사람들이 잘 모르는) 중에 하나이다. 단어의 category는 {category}이고 단어의 difficulty는 {difficulty}일 때, {category} 범주에 속하는 {difficulty} 하나의 단어를 생성해라. 이때 단어가 실존하는 단어인지, 한국어 단어인지, {category} 범주에 분류될 수 있는 단어인지, {difficulty} 단어인지 천천히 고심하여야 한다. 또한, 해당 단어 외에 어떤 것도 출력해서는 안 된다. 강조한다. 해당 단어 외에는 그 어떤 것도 출력되어서는 안 된다."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        result = response.choices[0].message['content']
        return result
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

# 정답 엔드포인트 정의
@app.get("/guess", response_model=dict)
async def guess_answer(guess: str = Query(...), word: str = Query(...), category: str = Query(...)):
    try:
        prompt = f"{guess}와 {word}가 동일한 {category}라고 생각해? 정확히 true 또는 false 둘 중 하나만 반환해."
        answer = get_chatgpt_response(prompt)
        return { "answer": answer }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# FastAPI 서버를 실행하는 부분
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
