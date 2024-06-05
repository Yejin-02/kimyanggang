from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
import openai
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI API 키 설정


# 정답 설정, 최대 질문 개수 설정
MAX_QUESTIONS = 20

# 게임 상태를 유지하기 위한 변수
class GameState:
    def __init__(self):
        self.is_active = True
        self.word = ""
        self.category = ""
        self.difficulty = ""
        self.questions_asked = 0

game_state = GameState()

class GameStartRequest(BaseModel):
    category: str
    difficulty: str

# 단어 생성 모델 호출 함수
def generate_word(category: str, difficulty: str) -> str:
    try:
        prompt = f"나는 스무고개 게임의 딜러이다. 스무고개 게임의 딜러는 단어를 고르는 역할을 한다. 스무고개 게임의 플레이어는 단어에 대한 질문을 한다. 딜러는 질문에 예/아니오로 답할 수 있다. 딜러는 플레이어가 원하는 category와 difficulty의 단어를 골라야 한다. category는 영화제목, 동식물, 노래제목, 장소, 음식 중에 하나이다. 딜러가 고르는 단어는 category의 예시 단어이고, 구체적인 실존 단어여야 한다. difficulty는 쉬운, 어려운 중에 하나이다. 쉬운 단어는 사람들이 자주 사용하는 단어이고 어려운 단어는 사람들이 잘 알지 못하는 단어이다. category가 '{category}'인 단어 중 '{difficulty}' 예시 단어를 골라야 해. 하나의 예시 단어만 단답형으로 출력해."
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
@app.post("/start_game")
async def start_game(request: GameStartRequest):
    game_state.category = request.category
    game_state.difficulty = request.difficulty
    game_state.word = generate_word(game_state.category, game_state.difficulty)
    game_state.is_active = True
    game_state.questions_asked = 0
    return {"message": "Game started", "category": game_state.category, "difficulty": game_state.difficulty, "word": game_state.word}

# 질문 엔드포인트 정의
@app.post("/ask", response_model=dict)
async def ask_question(question: str):
    if not game_state.is_active:
        return {"message": "The game is not active. Please start a new game."}

    if game_state.questions_asked >= MAX_QUESTIONS:
        game_state.is_active = False
        return {"message": "You have reached the maximum number of questions. The game is over."}

    try:
        prompt = f"'{game_state.word}'에 대한 질문: '{question}'. 예 아니오로만 대답해줘."
        answer = get_chatgpt_response(prompt)
        game_state.questions_asked += 1
        return {"question": question, "answer": answer, "questions_left": MAX_QUESTIONS - game_state.questions_asked}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 정답 맞추기 엔드포인트 정의
@app.post("/guess", response_model=dict)
async def guess_word(guess: str = Form(...)):
    if not game_state.is_active:
        return {"message": "The game is not active. Please start a new game."}

    if guess == game_state.word:
        game_state.is_active = False
        return {"result": "Correct!", "message": "Congratulations! You've guessed the correct word."}
    else:
        return {"result": "Incorrect", "message": "Try again!"}

# 게임 리셋 엔드포인트 정의
@app.post("/reset", response_model=dict)
async def reset_game():
    game_state.is_active = False
    game_state.word = ""
    game_state.category = ""
    game_state.difficulty = ""
    game_state.questions_asked = 0
    return {"message": "The game has been reset. You can start a new game."}

# FastAPI 서버를 실행하는 부분
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
