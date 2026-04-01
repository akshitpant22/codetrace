import React from "react";
import { Link, useLocation } from "react-router-dom";

const Navbar = () => {
  const { pathname } = useLocation();

  return (
    <header className="fixed top-0 w-full z-50 bg-[#131313]/80 backdrop-blur-xl border-b border-[#00ff9f]/10 shadow-[0_4px_20px_rgba(0,0,0,0.5)] flex justify-between items-center h-16 px-8 max-w-full">
      <Link to="/" className="text-2xl font-bold tracking-tighter text-[#00ff9f] drop-shadow-[0_0_8px_rgba(0,255,159,0.5)] font-headline hover:opacity-80 transition-opacity">
        CodeTrace
      </Link>

      <nav className="hidden md:flex gap-8 items-center">
        <Link
          to="/"
          className={`font-['Space_Grotesk'] uppercase tracking-widest text-sm transition-colors pb-1 border-b-2
            ${pathname === "/" ? "text-[#00ff9f] border-[#00ff9f]" : "text-gray-400 hover:text-[#00ff9f] border-transparent"}`}
        >
          Home
        </Link>
        <Link
          to="/features"
          className={`font-['Space_Grotesk'] uppercase tracking-widest text-sm transition-colors pb-1 border-b-2
            ${pathname === "/features" ? "text-[#00ff9f] border-[#00ff9f]" : "text-gray-400 hover:text-[#00ff9f] border-transparent"}`}
        >
          Features
        </Link>
      </nav>
    </header>
  );
};

export default Navbar;
