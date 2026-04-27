import React from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { Loader2 } from "lucide-react";
import Navbar from "./components/layout/Navbar";
import { AuthProvider, useAuth } from "./contexts/AuthContext";

import Home from "./pages/Home";
import Analyze from "./pages/Analyze";
import MultiAnalyze from "./pages/MultiAnalyze";
import History from "./pages/History";
import Features from "./pages/Features";
import RDPAnalyze from "./pages/RDPAnalyze";
import Benchmark from "./pages/Benchmark";

import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import VerifyOTP from "./pages/VerifyOTP";

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <Loader2 className="w-10 h-10 text-[#00ff9f] animate-spin" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

const App = () => {
  const location = useLocation();
  const authRoutes = ['/login', '/register', '/forgot-password', '/verify-otp'];
  const isAuthRoute = authRoutes.includes(location.pathname);

  return (
    <AuthProvider>
      <div className="min-h-screen bg-[#0a0a0f] text-white font-body">
        {!isAuthRoute && <Navbar />}
        <main className={`${isAuthRoute ? '' : 'pt-16'} min-h-screen`}>
          <Routes>
            
            <Route path="/" element={<Home />} />
            <Route path="/features" element={<Features />} />
            <Route path="/rdp-analyze" element={<RDPAnalyze />} />            
            <Route path="/benchmark" element={<Benchmark />} />
            
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/verify-otp" element={<VerifyOTP />} />

            
            <Route
              path="/analyze"
              element={
                <ProtectedRoute>
                  <Analyze />
                </ProtectedRoute>
              }
            />
            <Route
              path="/multi-analyze"
              element={
                <ProtectedRoute>
                  <MultiAnalyze />
                </ProtectedRoute>
              }
            />
            <Route
              path="/history"
              element={
                <ProtectedRoute>
                  <History />
                </ProtectedRoute>
              }
            />

            
            <Route path="*" element={<Home />} />
          </Routes>
        </main>
      </div>
    </AuthProvider>
  );
};

export default App;
