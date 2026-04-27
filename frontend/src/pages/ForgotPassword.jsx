import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Loader2, Code2, Cpu, ShieldCheck } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  const { forgotPassword } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    let timer;
    if (countdown > 0) {
      timer = setInterval(() => {
        setCountdown((prev) => prev - 1);
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [countdown]);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setIsLoading(true);

    try {
      await forgotPassword(email);
      setSuccess("OTP sent! Check your email.");
      setCountdown(30);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to send OTP. Please try again later."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    setError("");
    setSuccess("");
    try {
      await forgotPassword(email);
      setSuccess("OTP resent!");
      setCountdown(30);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to resend OTP.");
    }
  };

  return (
    <div className="min-h-screen flex text-white overflow-hidden bg-[#0d0d14]">
      
      <div 
        className="hidden lg:flex w-1/2 flex-col justify-center items-center relative p-12 bg-[#0a0a0f]"
        style={{
          backgroundImage: 'radial-gradient(circle at 2px 2px, #1e1e2e 1px, transparent 0)',
          backgroundSize: '32px 32px'
        }}
      >
        
        <div className="absolute w-[500px] h-[500px] bg-[#00ff9f]/10 rounded-full blur-[120px] pointer-events-none" />
        
        <div className="relative z-10 max-w-lg w-full flex flex-col items-center text-center">
          <div className="flex items-center gap-3 mb-6">
            <img src="/icon.svg" alt="CodeTrace" style={{ width: 64, height: 64 }} />
            <span className="text-5xl font-black tracking-tighter text-white">Code<span className="text-[#00ff9f]">Trace</span></span>
          </div>
          
          <h2 className="text-2xl font-semibold text-[#8888aa] mb-10 tracking-wide">
            Detect. Analyze. Protect.
          </h2>

          <div className="flex flex-wrap justify-center gap-4">
            <div className="flex items-center gap-2 bg-[#12121a]/80 border border-[#1e1e2e] backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium text-gray-300">
              <Cpu className="w-4 h-4 text-[#00ff9f]" /> 5-Stage Pipeline
            </div>
            <div className="flex items-center gap-2 bg-[#12121a]/80 border border-[#1e1e2e] backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium text-gray-300">
              <Code2 className="w-4 h-4 text-[#00ff9f]" /> AST Analysis
            </div>
            <div className="flex items-center gap-2 bg-[#12121a]/80 border border-[#1e1e2e] backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium text-gray-300">
              <ShieldCheck className="w-4 h-4 text-[#00ff9f]" /> Real-time Detection
            </div>
          </div>
        </div>
      </div>

      
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 relative">
        <style>
          {`
            @keyframes fadeInUp {
              from { opacity: 0; transform: translateY(20px); }
              to { opacity: 1; transform: translateY(0); }
            }
            .animate-fade-in-up {
              animation: fadeInUp 0.4s ease-out forwards;
            }
          `}
        </style>
        
        <div 
          className={`w-full max-w-md p-10 rounded-2xl opacity-0 ${isVisible ? 'animate-fade-in-up' : ''}`}
          style={{
            background: 'rgba(18, 18, 26, 0.8)',
            border: '1px solid rgba(255,255,255,0.08)',
            backdropFilter: 'blur(20px)',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
          }}
        >
          
          <div className="flex flex-col items-center mb-8">
            <div className="bg-[#00ff9f]/10 p-4 rounded-full mb-5 shadow-[0_0_20px_rgba(0,255,159,0.15)] border border-[#00ff9f]/20">
              <img src="/icon.svg" alt="CodeTrace" style={{ width: 64, height: 64 }} />
            </div>
            <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Forgot Password</h1>
            <p className="text-[#8888aa] text-sm text-center">Enter your email to receive a verification code</p>
          </div>

          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-[#8888aa] ml-1">Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-[#0a0a0f]/50 border border-[#1e1e2e] rounded-xl text-white placeholder-[#8888aa]/40 focus:outline-none focus:border-[#00ff9f] focus:ring-1 focus:ring-[#00ff9f] transition-all duration-300"
                placeholder="name@example.com"
              />
            </div>

            {error && (
              <div className="p-3 bg-red-900/20 border border-red-500/30 rounded-xl flex items-center gap-2 text-sm text-red-400">
                <ShieldCheck className="w-4 h-4 shrink-0" />
                <p>{error}</p>
              </div>
            )}

            {success && (
              <div className="p-3 bg-[#00ff9f]/10 border border-[#00ff9f]/30 rounded-xl flex items-center gap-2 text-sm text-[#00ff9f]">
                <ShieldCheck className="w-4 h-4 shrink-0" />
                <p>{success}</p>
              </div>
            )}

            {!success && countdown === 0 ? (
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3.5 px-4 bg-[#00ff9f] text-[#0a0a0f] font-bold rounded-xl transition-all duration-300 flex justify-center items-center gap-2 hover:bg-[#00e68f] hover:shadow-[0_0_20px_rgba(0,255,159,0.3)] disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:shadow-none"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Sending...
                  </>
                ) : (
                  "Send OTP"
                )}
              </button>
            ) : (
              <div className="flex flex-col gap-3">
                <button
                  type="button"
                  onClick={() => navigate("/verify-otp", { state: { email } })}
                  className="w-full py-3.5 px-4 bg-[#12121a] text-white border border-[#1e1e2e] font-bold rounded-xl transition-all duration-300 hover:bg-[#1e1e2e]"
                >
                  Enter Verification Code
                </button>
                <button
                  type="button"
                  disabled={countdown > 0}
                  onClick={handleResend}
                  className="w-full py-3.5 px-4 border border-[#00ff9f] text-[#00ff9f] font-bold rounded-xl transition-all duration-300 flex justify-center items-center gap-2 hover:bg-[#00ff9f]/10 disabled:opacity-50 disabled:cursor-not-allowed disabled:border-gray-600 disabled:text-gray-500"
                >
                  {countdown > 0 ? `Resend OTP in ${countdown}s` : "Resend OTP"}
                </button>
              </div>
            )}
          </form>

          
          <div className="mt-8 flex items-center justify-center gap-4">
            <div className="h-px bg-[#1e1e2e] flex-1"></div>
            <span className="text-xs text-[#8888aa] uppercase tracking-widest font-semibold">or</span>
            <div className="h-px bg-[#1e1e2e] flex-1"></div>
          </div>

          
          <div className="mt-8 text-center text-sm text-[#8888aa]">
            Remember your password?{" "}
            <Link 
              to="/login" 
              className="font-semibold text-white hover:text-[#00ff9f] transition-colors"
            >
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
