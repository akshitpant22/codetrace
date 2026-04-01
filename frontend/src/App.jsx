import React from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/layout/Navbar";
import Analyze from "./pages/Analyze";
import Features from "./pages/Features";

const App = () => {
  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white font-body">
      <Navbar />
      <main className="pt-16 min-h-screen">
        <Routes>
          <Route path="/"         element={<Analyze />} />
          <Route path="/features" element={<Features />} />
          <Route path="*"         element={<Analyze />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
