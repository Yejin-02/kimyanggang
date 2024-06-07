import { useNavigate } from "react-router-dom";
import React, { FormEvent, useRef, useState } from "react";
import './../styles/Home.css';

let Home: React.FC = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false); // 로딩 상태를 관리하는 state

    const handleSubmit = async (event: FormEvent) => {
        event.preventDefault();

        if(diffRef.current && cateRef.current) {
            const difficulty = diffRef.current.value;
            const category = cateRef.current.value;

            setLoading(true); // 로딩 시작
            
            try {
                const response = await fetch(`http://127.0.0.1:8000/start_game?category=${category}&difficulty=${difficulty}`, {
                    method: 'GET',
                });
                const data = await response.json();// 서버로부터 받은 단어 설정
                console.log(data.word);
                if (data.word) {
                    const gameWord = data.word;
                    navigate('/gamestart', { state: { difficulty, category, gameWord } });
                } else {
                    // gameWord가 undefined이거나 null인 경우
                    console.error('Game word is undefined or null');
                }
            } catch (error) {
                console.error('Error fetching game word:', error);
            } finally {
                setLoading(false);
            }
        }
    };

    const diffRef = useRef<HTMLSelectElement>(null);
    const cateRef = useRef<HTMLSelectElement>(null);
    
    return (
        <div className="Home">
            <p>스무고개 생성기에 오신 것을 환영합니다.</p>
            <p>스무고개는 예/아니오로 답변할 수 있는 20개의 질문을 하고, 답변에 따라 단어를 추측하는 게임입니다.</p>
            <p>게임을 시작하기 위해 게임의 난이도와 단어의 범주를 고르세요.</p>
            
            <form onSubmit={handleSubmit}>
                <label>
                    게임 난이도:
                    <select ref={diffRef} id="difficulty" name="difficulty">
                        <option value="쉬운">쉬운 모드</option>
                        <option value="어려운">어려운 모드</option>
                    </select>
                </label>
                <br />
                <label>
                    단어 범주:
                    <select ref={cateRef} id="category" name="category">
                        <option value="영화 제목">영화 제목</option>
                        <option value="동식물">동식물</option>
                        <option value="지역 이름">지역 이름</option>
                        <option value="음식 메뉴">음식</option>
                        <option value="사물">사물</option>
                    </select>
                </label>
                <br />
                <button type="submit">Game Start</button>
            </form>
            {loading && <div className="modal-overlay">
                            <div className="modal-content">
                                <p>Loading...</p>
                            </div>
                        </div>}
        </div>
    );
}

export default Home;