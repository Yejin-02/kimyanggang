import { useNavigate } from "react-router-dom";
import React, { FormEvent, useRef } from "react";
import './../styles/Home.css';

let Home: React.FC = () => {
    const navigate = useNavigate();
    
    const handleSubmit = (event: FormEvent) => {
        event.preventDefault();
        if(diffRef.current && cateRef.current) {
            const difficulty = diffRef.current.value;
            const category = cateRef.current.value;
            navigate('/gamestart', { state: { difficulty, category } });
        }
    };

    const diffRef = useRef<HTMLSelectElement>(null);
    const cateRef = useRef<HTMLSelectElement>(null);
    
    return (
        <div className="Home">
            <p>스무고개 생성기에 오신 것을 환영합니다.</p>
            <p>스무고개 게임은 예/아니오로 답변할 수 있는 20개의 질문을 하고, 답변에 따라 단어를 추측하는 게임입니다.</p>
            <p>게임을 시작하기 위해 단어의 분류와 난이도를 고르세요.</p>
            
            <form onSubmit={handleSubmit}>
                <label>
                    난이도:
                    <select ref={diffRef} id="difficulty" name="difficulty">
                        <option value="쉬움">일반 모드</option>
                        <option value="어려움">하드 모드</option>
                    </select>
                </label>
                <br />
                <label>
                    분류:
                    <select ref={cateRef} id="category" name="category">
                        <option value="영화제목">영화제목</option>
                        <option value="동식물">동식물</option>
                        <option value="노래제목">노래제목</option>
                        <option value="장소">장소</option>
                        <option value="음식">음식</option>
                    </select>
                </label>
                <br />
                <button type="submit">Game Start</button>
            </form>

        </div>
    );
}

export default Home;