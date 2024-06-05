import { Link } from "react-router-dom";
import React from "react";
import './../styles/Header.css';

let Header = () => {
    return (
        <div className="header">
            <h1>
                <Link to="/">스무고개 생성기</Link>
            </h1>
        </div>
    );
}

export default Header;