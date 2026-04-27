import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Terminal, 
  Cpu, 
  Fingerprint, 
  GitBranch, 
  Network, 
  Upload, 
  Bot, 
  BarChart, 
  Code2, 
  Zap,
  ArrowRight
} from 'lucide-react';

const Home = () => {
  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white font-sans selection:bg-[#00ff9f]/30">
      
      {/* 1. HERO SECTION */}
      <section className="pt-32 pb-24 px-6 flex flex-col items-center justify-center text-center">
        <div className="max-w-4xl mx-auto flex flex-col items-center">
          <h1 className="text-5xl md:text-7xl font-semibold mb-6 tracking-tight">
            <span className="text-[#00ff9f]">Code</span>
            <span className="text-white">Trace</span>
          </h1>
          
          <p className="text-xl md:text-2xl text-[#8888aa] max-w-2xl mb-8 font-light tracking-tight">
            AI-Powered Code Plagiarism Detection
          </p>
          
          <p className="text-base text-[#8888aa] max-w-2xl mb-12 leading-relaxed">
            Protect your intellectual property with absolute precision. 
            Our detection pipeline analyzes lexical, syntactic, and semantic code structures to identify complex obfuscation and duplicate code.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
            <Link 
              to="/analyze" 
              className="flex items-center justify-center gap-2 px-6 py-3 bg-[#00ff9f] text-black font-medium rounded-md hover:bg-[#00e68f] transition-colors"
            >
              Start Analyzing
              <ArrowRight size={18} />
            </Link>
            
            <Link 
              to="/multi-analyze" 
              className="flex items-center justify-center gap-2 px-6 py-3 bg-transparent text-white border border-[#1e1e2e] font-medium rounded-md hover:bg-white/5 transition-colors"
            >
              Multi-File Analysis
            </Link>
          </div>
        </div>
      </section>

      {/* 2. STATS SECTION */}
      <section className="border-y border-[#1e1e2e] bg-[#0a0a0f]">
        <div className="max-w-5xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-[#1e1e2e]">
          <div className="py-8 flex flex-col items-center justify-center">
            <span className="text-3xl font-semibold text-white mb-1 tracking-tight">5 Stage</span>
            <span className="text-sm text-[#8888aa]">Detection Pipeline</span>
          </div>
          <div className="py-8 flex flex-col items-center justify-center">
            <span className="text-3xl font-semibold text-white mb-1 tracking-tight">3+</span>
            <span className="text-sm text-[#8888aa]">Languages Supported</span>
          </div>
          <div className="py-8 flex flex-col items-center justify-center">
            <span className="text-3xl font-semibold text-[#00ff9f] mb-1 tracking-tight">99%</span>
            <span className="text-sm text-[#8888aa]">Detection Accuracy</span>
          </div>
        </div>
      </section>

      {/* 3. HOW IT WORKS SECTION */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="mb-16">
            <h2 className="text-2xl font-semibold text-white tracking-tight mb-2">How It Works</h2>
            <p className="text-[#8888aa]">A seamless pipeline from code submission to deep analysis.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 md:gap-8">
            {[
              { step: "01", title: "Upload Code Files", desc: "Securely upload your source code via our encrypted gateway. Single pairs or bulk batch processing supported.", icon: <Upload size={18} className="text-white" /> },
              { step: "02", title: "AI Analysis Runs", desc: "Our neural architecture deconstructs code into Abstract Syntax Trees and Dependency Graphs.", icon: <Bot size={18} className="text-white" /> },
              { step: "03", title: "Get Similarity Score", desc: "Receive an immediate, comprehensive breakdown of lexical, structural, and semantic matches.", icon: <BarChart size={18} className="text-[#00ff9f]" /> }
            ].map((item, i) => (
              <div key={i} className="flex flex-col border-t border-[#1e1e2e] pt-6">
                <div className="flex items-center gap-4 mb-5">
                  <span className="text-sm font-mono text-[#8888aa]">{item.step}</span>
                  <div className="w-8 h-8 rounded border border-[#1e1e2e] flex items-center justify-center">
                    {item.icon}
                  </div>
                </div>
                <h4 className="text-lg font-medium text-white mb-2 tracking-tight">{item.title}</h4>
                <p className="text-sm text-[#8888aa] leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 4. FEATURES SECTION */}
      <section className="py-24 px-6 border-t border-[#1e1e2e] bg-[#0a0a0f]">
        <div className="max-w-5xl mx-auto">
          <div className="mb-16">
            <h2 className="text-2xl font-semibold text-white tracking-tight mb-2">Core Technologies</h2>
            <p className="text-[#8888aa]">Advanced analysis techniques powering our engine.</p>
          </div>
          
          {/* Top Row: 2 items */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            {[
              { title: "Lexical Analysis", desc: "Winnowing algorithm fingerprints code sequences, ignoring superficial changes like comments or whitespace.", icon: <Code2 size={18} /> },
              { title: "Syntax Analysis", desc: "AST comparison maps the structural integrity of the code, detecting rearranged functions and renamed variables.", icon: <Fingerprint size={18} /> }
            ].map((feature, i) => (
              <div key={`top-${i}`} className="p-6 border border-[#1e1e2e] rounded-md hover:bg-white/[0.02] transition-colors">
                <div className="mb-4 text-[#8888aa]">
                  {feature.icon}
                </div>
                <h4 className="text-base font-medium text-white mb-2 tracking-tight">{feature.title}</h4>
                <p className="text-sm text-[#8888aa] leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>

          {/* Bottom Row: 3 items */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { title: "Semantic Analysis", desc: "Halstead complexity metrics and entropy calculations to find deeper logic similarities and code cloning.", icon: <Cpu size={18} /> },
              { title: "Control Flow Graph", desc: "Tracks execution paths and branching logic to identify plagiarized algorithms despite control structure modifications.", icon: <GitBranch size={18} /> },
              { title: "Program Dependence", desc: "Advanced PDG mapping analyzes how data flows through variables to catch the most sophisticated obfuscation.", icon: <Zap size={18} /> }
            ].map((feature, i) => (
              <div key={`bottom-${i}`} className="p-6 border border-[#1e1e2e] rounded-md hover:bg-white/[0.02] transition-colors">
                <div className="mb-4 text-[#8888aa]">
                  {feature.icon}
                </div>
                <h4 className="text-base font-medium text-white mb-2 tracking-tight">{feature.title}</h4>
                <p className="text-sm text-[#8888aa] leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

    </div>
  );
};

export default Home;
