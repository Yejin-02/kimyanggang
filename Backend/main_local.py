from fastapi import FastAPI, HTTPException, Query, Form
from pydantic import BaseModel
import openai

app = FastAPI()

# OpenAI API 키 설정
OPENAI_API_KEY = "sk-proj-FvTMBN2tJOJaeQN6JNZaT3BlbkFJX7iYFEUtxiAOofF6YURj"
openai.api_key = OPENAI_API_KEY

# 정답 설정, 최대 질문 개수 설정
ANSWER = ""
MAX_QUESTIONS = 20

# 게임 상태를 유지하기 위한 변수
class GameState:
    def __init__(self):
        self.is_active = True
        self.answer = ""
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
        prompt = f"Generate a {difficulty} word for the category {category}."
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
    game_state.answer = generate_word(game_state.category, game_state.difficulty)
    game_state.is_active = True
    game_state.questions_asked = 0
    return {"message": "Game started", "category": game_state.category, "difficulty": game_state.difficulty, "answer": game_state.answer}

# 질문 엔드포인트 정의
@app.get("/ask", response_model=dict)
async def ask_question(question: str = Query(..., title="Question", description="Enter your question")):
    if not game_state.is_active:
        return {"message": "The game is not active. Please start a new game."}

    if game_state.questions_asked >= MAX_QUESTIONS:
        game_state.is_active = False
        return {"message": "You have reached the maximum number of questions. The game is over."}

    try:
        prompt = f"{game_state.answer}에 대한 질문: '{question}' 예 아니오로만 대답해주세요."
        answer = get_chatgpt_response(prompt)
        game_state.questions_asked += 1
        return {"question": question, "answer": answer, "questions_left": MAX_QUESTIONS - game_state.questions_asked}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 정답 맞추기 엔드포인트 정의
@app.post("/guess", response_model=dict)
async def guess_answer(guess: str = Form(...)):
    if not game_state.is_active:
        return {"message": "The game is not active. Please start a new game."}

    if guess == game_state.answer:
        game_state.is_active = False
        return {"result": "Correct!", "message": "Congratulations! You've guessed the correct answer."}
    else:
        return {"result": "Incorrect", "message": "Try again!"}

# 게임 리셋 엔드포인트 정의
@app.post("/reset", response_model=dict)
async def reset_game():
    game_state.is_active = False
    game_state.answer = ""
    game_state.category = ""
    game_state.difficulty = ""
    game_state.questions_asked = 0
    return {"message": "The game has been reset. You can start a new game."}

# FastAPI 서버를 실행하는 부분
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
