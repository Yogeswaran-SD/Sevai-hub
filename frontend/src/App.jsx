import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import ChatAssistant from "./components/ChatAssistant";
import Home from "./pages/Home";
import Search from "./pages/Search";
import Intelligence from "./pages/Intelligence";

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/"             element={<Home />} />
        <Route path="/search"       element={<Search />} />
        <Route path="/intelligence" element={<Intelligence />} />
      </Routes>
      <ChatAssistant />
    </BrowserRouter>
  );
}
