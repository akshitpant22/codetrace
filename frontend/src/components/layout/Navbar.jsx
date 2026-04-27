import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

const Navbar = () => {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <header className="fixed top-0 w-full z-50 bg-[#131313]/80 backdrop-blur-xl border-b border-[#00ff9f]/10 shadow-[0_4px_20px_rgba(0,0,0,0.5)] flex justify-between items-center h-16 px-8 max-w-full">
      
      <div className="flex-1">
        <Link to="/" className="text-2xl font-bold tracking-tighter text-[#00ff9f] drop-shadow-[0_0_8px_rgba(0,255,159,0.5)] font-headline hover:opacity-80 transition-opacity">
          CodeTrace
        </Link>
      </div>

      
      <nav className="hidden md:flex flex-none gap-8 items-center">
        <Link
          to="/"
          className={`font-['Space_Grotesk'] uppercase tracking-widest text-sm transition-colors pb-1 border-b-2
            ${pathname === "/" ? "text-[#00ff9f] border-[#00ff9f]" : "text-gray-400 hover:text-[#00ff9f] border-transparent"}`}
        >
          Home
        </Link>
        <Link
          to="/analyze"
          className={`font-['Space_Grotesk'] uppercase tracking-widest text-sm transition-colors pb-1 border-b-2
            ${pathname === "/analyze" ? "text-[#00ff9f] border-[#00ff9f]" : "text-gray-400 hover:text-[#00ff9f] border-transparent"}`}
        >
          Analyze
        </Link>
        <Link
          to="/multi-analyze"
          className={`font-['Space_Grotesk'] uppercase tracking-widest text-sm transition-colors pb-1 border-b-2
            ${pathname === "/multi-analyze" ? "text-[#00ff9f] border-[#00ff9f]" : "text-gray-400 hover:text-[#00ff9f] border-transparent"}`}
        >
          Multi-Analyze
        </Link>
        <Link
          to="/history"
          className={`font-['Space_Grotesk'] uppercase tracking-widest text-sm transition-colors pb-1 border-b-2
            ${pathname === "/history" ? "text-[#00ff9f] border-[#00ff9f]" : "text-gray-400 hover:text-[#00ff9f] border-transparent"}`}
        >
          History
        </Link>
        <Link
          to="/rdp-analyze"
          className={`font-['Space_Grotesk'] uppercase tracking-widest text-sm transition-colors pb-1 border-b-2
            ${pathname === "/rdp-analyze" ? "text-[#00ff9f] border-[#00ff9f]" : "text-gray-400 hover:text-[#00ff9f] border-transparent"}`}
        >
          RDP Parser
        </Link>
        <Link
          to="/benchmark"
          className={`font-['Space_Grotesk'] uppercase tracking-widest text-sm transition-colors pb-1 border-b-2
            ${pathname === "/benchmark" ? "text-[#00ff9f] border-[#00ff9f]" : "text-gray-400 hover:text-[#00ff9f] border-transparent"}`}
        >
          Benchmark
        </Link>
      </nav>

      
      <div className="flex-1 flex justify-end items-center gap-4">
        {user ? (
          <>
            <span className="hidden sm:inline text-sm font-medium text-[#8888aa]">
              {user.email}
            </span>
            <button
              onClick={handleLogout}
              className="px-4 py-1.5 text-sm font-semibold text-white border border-[#1e1e2e] bg-[#1a1a24] hover:border-[#00ff9f]/50 hover:text-[#00ff9f] rounded transition-colors"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link
              to="/login"
              className="px-4 py-1.5 text-sm font-semibold text-[#00ff9f] border border-[#00ff9f] rounded hover:bg-[#00ff9f]/10 transition-colors"
            >
              Login
            </Link>
            <Link
              to="/register"
              className="px-4 py-1.5 text-sm font-semibold text-black bg-[#00ff9f] hover:bg-[#00cc7f] rounded transition-colors"
            >
              Register
            </Link>
          </>
        )}
      </div>
    </header>
  );
};

export default Navbar;
