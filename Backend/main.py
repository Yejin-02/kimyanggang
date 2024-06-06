from fastapi import FastAPI, HTTPException, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai

app = FastAPI()

# OpenAI API 키 설정
OPENAI_API_KEY = "API_KEY_HERE"
openai.api_key = OPENAI_API_KEY

# 정답 설정, 최대 질문 개수 설정
ANSWER = ""
MAX_QUESTIONS = 20

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 프론트엔드 도메인을 추가
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# 단어 유효성 검사 함수
def is_valid_word(word: str, category: str) -> bool:
    # GPT를 통해 단어 유효성을 검증
    prompt = f"'{word}'가 다음 세 가지 조건을 모두 만족하면 '예', 그렇지 않으면 '아니오'로 대답해줘: 첫째, '{word}'는 한 단어이다. 둘째, '{word}'는 실제로 존재하는 단어이다. 셋째, '{word}'는 '{category}' 중 하나이다."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        answer = response.choices[0].message['content'].strip().lower()
        return answer == "예" or answer == "yes"
    except openai.OpenAIError as e:
        raise HTTPException(status_code=500, detail=str(e))

# 단어 생성 모델 호출 함수
def generate_word(category: str, difficulty: str) -> str:
    attempt = 0
    max_attempts = 20
    while attempt < max_attempts:
        try:
            prompt = f"임의로 단어를 하나 골라줘. 이 두 가지 조건을 만족하는 단어여야 해: 첫째, '{category}'중 하나여야 해. 둘째, 난이도는 '{difficulty}'이야. 난이도가 '쉬운' 일 경우 유명한 단어여야 해. 난이도가 '어려운'일 경우 유명하지 않은 단어여야 해. 정확히 한 단어만 골라서 단답식으로 대답해줘."
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            word = response.choices[0].message['content'].strip()
            if is_valid_word(word, category):
                return word
        except openai.OpenAIError as e:
            raise HTTPException(status_code=500, detail=str(e))
        attempt += 1
    raise HTTPException(status_code=500, detail="Valid word could not be generated after multiple attempts")

"""
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
"""

# 게임 시작 엔드포인트 정의
@app.get("/api/v1/start_game")
async def start_game(category: str = Query(...), difficulty: str = Query(...)):
    word = generate_word(category, difficulty)
    return {"message": "Game started", "category": category, "difficulty": difficulty, "word": word}

# 질문 엔드포인트 정의
@app.get("/api/v1/ask", response_model=dict)
async def ask_question(question: str = Query(...), word: str = Query(...)):
    try:
        prompt = f"'{word}'에 대한 질문: '{question}'. 예 아니오로만 대답해줘."
        answer = get_chatgpt_response(prompt)
        return {"question": question, "answer": answer}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 정답 맞추기 엔드포인트 정의
@app.get("/api/v1/guess", response_model=dict)
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
