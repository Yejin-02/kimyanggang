import React, { useState, useEffect } from "react";
import { useLocation } from 'react-router-dom';
import './../styles/GameStart.css';

export interface GameState {
    difficulty: string;
    category: string;
    count: number;
}

let GameStart: React.FC = () => {
    // Home.tsx에서 diff, cate 받아오기
    const location = useLocation();
    const { difficulty, category } = location.state as GameState;

    // 게임 상태 관리
    const [isGameOver, setIsGameOver] = useState<boolean>(false); // 게임이 끝났는지 체크
    const [isRight, setIsRight] = useState<boolean>(true); // 정답을 맞췄는지 체크
    const [result, setResult] = useState<string>(''); // isRight에 따라 출력 메세지 관리
    const [questionsAsked , setQuestionsAsked] = useState<number>(1); // 질문 횟수 카운트

    // 질문 제출 관리
    const [questions, setQuestions] = useState<string[]>([]); // 질문 입력 받으면 배열에 저장
    const [answers, setAnswers] = useState<string[]>([]); // 질문에 대한 답변도 배열에 저장
    const [currentQuestion, setCurrentQuestion] = useState<string>(''); // 현재 질문

    // 단어 제출 관리
    const [gameWord, setGameWord] = useState<string>(''); // 게임 단어 저장
    const [userGuess, setUserGuess] = useState<string>(''); // user의 추측 단어를 저장

    // 초기에 게임 단어 설정
    useEffect(() => {
        const fetchGameWord = async () => {
            try {
                const response = await fetch('http://127.0.0.1:8000/start_game', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ category: category, difficulty: difficulty }),
                });    
                console.log('여기까지');
                const data = await response.json();
                setGameWord(data.word); // 서버로부터 받은 단어 설정
            } catch (error) {
                console.error('Error fetching game word:', error);
                setGameWord('default'); // 에러 발생 시 기본 단어 설정
            }
        };
        fetchGameWord();
      }, [difficulty, category]);

    // 질문 제출 버튼 클릭 -> 질문 제출 관리
    const handleQuestionSubmit = async () => {
        if (currentQuestion.trim() === '') return;
    
        // 20개까지만 질문할 수 있음
        if (questions.length < 20) {
            // 질문 횟수 +1, 질문을 배열에 저장
            setQuestionsAsked(questionsAsked+1);
            setQuestions([...questions, currentQuestion]);

            // ChatGPT 이용하여 답변 받아오기
            try {
                const response = await fetch('http://127.0.0.1:8000/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type' : 'application/json',
                    },
                    body: JSON.stringify( {question: currentQuestion} ),
                });

                const data = await response.json();
                const answer = data.answer;

                setAnswers([...answers, answer]);
            } catch (error) {
                console.error('Error fetching answer: ', error);
                setAnswers([...answers, 'not sure']);
            }
            setCurrentQuestion('');
        } else {
            setIsGameOver(true); // 20개 넘어서부터는 게임 종료
        }
    };
    
    // 단어 제출 버튼 클릭 -> 단어 제출 관리
    const handleGuessSubmit = async () => {
        // user의 Guess와 game의 Word가 같은지 체크 -> Result 메세지 관리
        if (userGuess.trim().toLowerCase() === gameWord.toLowerCase()) {
            setResult('맞췄습니다! 정답은 ' + gameWord + '였습니다.');
            setIsRight(true);
        } else {
            setResult('틀렸습니다! 정답은 ' + gameWord + '였습니다.');
            setIsRight(false);
        }
        setIsGameOver(true);
        try {
            const response = await fetch('http://localhost:8000/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            console.log(data.message);  // 백엔드 응답 메시지 로그 출력
        } catch (error) {
            console.error('Error:', error);
        }
    };
    
    // 게임 끝난 후 출력할 내용 결정
    if (isGameOver) {
        return (
            <div>
                {isRight ? <h1>Congratulations!</h1> : <h1>Game Over</h1>}
                <p>{result}</p>
            </div>
        );
    }

    return (
        <div className="GameStart">
            <div className="wrap">
                <div className="GameState">
                    <h2>게임 상태</h2>
                    <p>난이도: {difficulty}</p>
                    <p>분류: {category}</p>
                    <p>남은 기회: {21-questionsAsked}</p>
                    <p>단어: {gameWord}</p>
                </div>
            </div>
            <br />
            <div className="GamePlay">
                <div className="GameQnA">
                    <h2>질문을 입력하세요</h2>
                    {questions.map((question, index) => (
                    <div key={index}>
                        <p>{question}</p>
                        <p>응답: {answers[index]}</p>
                    </div>
                    ))}
                    {questions.length < 20 && (
                    <div>
                        <input
                            type="text"
                            value={currentQuestion}
                            onChange={(e) => setCurrentQuestion(e.target.value)}
                            placeholder="Type your question"
                        />
                        <button onClick={handleQuestionSubmit}>질문 제출</button>
                    </div>
                    )}
                </div>
                <div className="wordSubmit">
                    <h2>단어를 추측하세요</h2>
                    <input
                        type="text"
                        value={userGuess}
                        onChange={(e) => setUserGuess(e.target.value)}
                        placeholder="What is the word?"
                    />
                    <button onClick={handleGuessSubmit}>단어 제출</button>
                </div>
            </div>
        </div>
    );
}


export default GameStart;