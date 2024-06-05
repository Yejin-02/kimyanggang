import {BrowserRouter, Routes, Route} from 'react-router-dom';
import EmptyPage from './component/EmptyPage.tsx';
import GameStart from './component/GameStart.tsx';
import Home from './component/Home.tsx';
import Header from './component/Header.tsx';
import React from "react";

import './App.css';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Header/>
        <Routes>
          <Route path='/' element={<Home />}/>
          <Route path="/gamestart" element={<GameStart />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
