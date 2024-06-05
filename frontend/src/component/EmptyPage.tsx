import { Link } from "react-router-dom";
import React from "react";

let EmptyPage = () => {
    return(
    <div className="emptyPage">
    <h3>빈 페이지입니다.</h3>
    <Link to="/">홈 화면으로 돌아가기</Link>
    </div>
    );
}

export default EmptyPage;