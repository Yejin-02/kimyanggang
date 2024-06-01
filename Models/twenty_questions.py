from typing import Literal

from pydantic import BaseModel, Field

# InputModel: game 시작 전 분야와 llm type을 고름
# OutputModel: game 시작하며 룰 설명
# InputQuestionModel: game 시작 후 user가 제시어에 대한 질문 입력
# OutputAnswerModel: user의 질문에 대해 예/아니오로 답변
# GameStateModel: game의 진행 상황을 저장

class InputModel(BaseModel):
    category: Literal['한국 영화', '외국 영화', '한국 가수', '동식물', '유명인'] = Field(
        description='퀴즈 분야',
        default='동식물',
    )
    level: Literal['하', '중', '상'] = Field(
        description='게임 난이도',
        default='하',
    )
    llm_type: Literal['chatgpt', 'huggingface'] = Field(
        alias='Large Language Model Type',
        description='사용할 LLM 종류',
        default='chatgpt',
    )
    question: str = Field(
        default='노란색이야?',
    )


class OutputModel(BaseModel):
    output: str = Field(
        description='응답',
    )
    
class GameStateModel(BaseModel):
    word: str = Field(
        description='게임 단어',
    )
    questionNumber: int = Field(
        description='질문 개수',
    )