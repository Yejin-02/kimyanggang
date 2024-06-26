from fastapi import HTTPException, Query, APIRouter
import openai

router = APIRouter(
    tags=['functions'],
)

OPENAI_API_KEY = ""
openai.api_key = OPENAI_API_KEY


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
@router.get("/api/v1/start_game")
async def start_game(category: str = Query(...), difficulty: str = Query(...)):
    word = generate_word(category, difficulty)
    return {"message": "Game started", "category": category, "difficulty": difficulty, "word": word}

# 질문 엔드포인트 정의
@router.get("/api/v1/ask", response_model=dict)
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
@router.get("/api/v1/guess", response_model=dict)
async def guess_answer(guess: str = Query(...), word: str = Query(...), category: str = Query(...)):
    try:
        prompt = f"{guess}와 {word}가 동일한 {category}라고 생각해? 정확히 true 또는 false 둘 중 하나만 반환해."
        answer = get_chatgpt_response(prompt)
        return { "answer": answer }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))