import React, { useState } from "react";

const FEATURES = [
  {
    icon: "🔤",
    title: "Lexical Analysis",
    tag: "Stage 1",
    tagColor: "#00ff9f",
    desc: "Tokenizes source code and computes token-level similarity using SequenceMatcher. Catches direct copy-paste and minor variable renames instantly.",
    bullets: [
      "Language-aware tokenization (Python, C, C++, Java, JS)",
      "Normalized token sequences — ignores whitespace & comments",
      "SequenceMatcher ratio gives 0–100 similarity score",
      "Detects: exact copies, renamed variables, reformatted code",
    ],
  },
  {
    icon: "🌳",
    title: "Syntax Analysis",
    tag: "Stage 2",
    tagColor: "#7000ff",
    desc: "Parses code into an Abstract Syntax Tree (AST) and builds a structural fingerprint of the program. Uncovers structural plagiarism even when names and logic differ.",
    bullets: [
      "Python: built-in ast module for precise parsing",
      "C / C++ / Java: Tree-sitter for accurate grammar-based ASTs",
      "Structural fingerprint: ordered list of node type labels",
      "Detects: restructured code, extracted functions, reordered blocks",
    ],
  },
  {
    icon: "🧠",
    title: "Semantic Analysis",
    tag: "Stage 3",
    tagColor: "#facc15",
    desc: "Extracts a semantic feature vector from operator patterns, control flow, and function calls. Uses cosine similarity to compare what the code *does*, not how it looks.",
    bullets: [
      "Operator patterns: arithmetic, logical, bitwise, augmented",
      "Control flow: if/else chains, loops, try/catch, switch",
      "Function call fingerprinting (Python: exact names; C/Java: generic)",
      "Cosine similarity on high-dimensional feature vectors",
    ],
  },
  {
    icon: "⚖️",
    title: "Weighted Final Score",
    tag: "Pipeline",
    tagColor: "#f87171",
    desc: "All three stages feed into a single weighted final score. Semantic and syntax stages are weighted higher since they are harder to fool.",
    bullets: [
      "Lexical: 20% weight",
      "Syntax:  40% weight",
      "Semantic: 40% weight",
      "Final score continuously saved to PostgreSQL/SQLite database",
    ],
  },
  {
    icon: "⚡",
    title: "Monaco Code Editor",
    tag: "UI",
    tagColor: "#00ff9f",
    desc: "Dual Monaco editors (same engine as VS Code) with syntax highlighting, line numbers, and smooth 3D perspective effects. Supports drag-to-upload and paste.",
    bullets: [
      "Full VS Code Monaco editor — syntax highlighting for all languages",
      "3D perspective tilt on focus for visual depth",
      "Drag & drop or click-to-upload source files",
      "Language selector: Python, C, C++, Java, JavaScript",
    ],
  },
  {
    icon: "📊",
    title: "Animated Results",
    tag: "UI",
    tagColor: "#7000ff",
    desc: "Score ring with animated count-up, neon glow, and a Recharts bar chart comparing all three detection stages at a glance.",
    bullets: [
      "SVG score ring with animated count-up (cubic ease-out)",
      "Color-coded: green < 30%, yellow 30–70%, red ≥ 70%",
      "Per-stage breakdown: Lexical / Syntax / Semantic pills",
      "Recharts BarChart with custom tooltip and glow effects",
    ],
  },
];

const FeatureCard = ({ feat, index }) => {
  const [hovered, setHovered] = useState(false);
  return (
    <div
      className="relative rounded-2xl p-7 border transition-all duration-300 cursor-default"
      style={{
        background: hovered ? "#12121a" : "#0e0e17",
        border: `1px solid ${hovered ? feat.tagColor + "44" : "#1e1e2e"}`,
        boxShadow: hovered ? `0 0 32px ${feat.tagColor}18, 0 12px 40px #00000066` : "0 4px 20px #00000044",
        transform: hovered ? "translateY(-4px)" : "translateY(0)",
        animationDelay: `${index * 0.08}s`,
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <span
        className="inline-block text-[10px] font-mono uppercase tracking-widest px-3 py-1 rounded-full mb-4"
        style={{ background: feat.tagColor + "18", color: feat.tagColor, border: `1px solid ${feat.tagColor}33` }}
      >
        {feat.tag}
      </span>

      <div className="flex items-center gap-3 mb-3">
        <span className="text-3xl">{feat.icon}</span>
        <h3 className="text-white font-bold text-xl font-headline">{feat.title}</h3>
      </div>

      <p className="text-[#8888aa] text-sm leading-relaxed mb-5">{feat.desc}</p>

      <ul className="space-y-2">
        {feat.bullets.map((b, i) => (
          <li key={i} className="flex items-start gap-2 text-xs text-[#a0a0c0]">
            <span className="mt-0.5 text-[8px]" style={{ color: feat.tagColor }}>▶</span>
            {b}
          </li>
        ))}
      </ul>
    </div>
  );
};

const Features = () => (
  <div className="min-h-screen bg-[#0a0a0f] px-4 py-16">
    <div className="text-center max-w-3xl mx-auto mb-16">
      <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[#00ff9f33] bg-[#00ff9f11] text-[#00ff9f] text-xs font-mono tracking-widest uppercase mb-6 shadow-[0_0_20px_#00ff9f22]">
        <span className="w-1.5 h-1.5 rounded-full bg-[#00ff9f] animate-pulse" />
        Detection Pipeline
      </div>
      <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-5 tracking-tight font-headline">
        How <span className="neon-green">CodeTrace</span> Works
      </h1>
      <p className="text-[#b0b0d0] text-lg leading-relaxed">
        A 3-stage detection pipeline combining lexical tokens, AST structure, and
        semantic feature vectors to catch plagiarism at every level.
      </p>
    </div>

    <div className="max-w-5xl mx-auto mb-16 flex items-center justify-center gap-0 text-sm font-mono">
      {["Lexical (20%)", "→", "Syntax (40%)", "→", "Semantic (40%)", "→", "Final Score"].map((step, i) => (
        <span
          key={i}
          className={`px-4 py-2 rounded-lg text-xs uppercase tracking-widest ${
            step === "→"
              ? "text-[#3a3a5a] px-2"
              : i === 12
              ? "bg-[#00ff9f] text-[#0a0a0f] font-bold"
              : "bg-[#12121a] border border-[#1e1e2e] text-[#8888aa]"
          }`}
        >
          {step}
        </span>
      ))}
    </div>

    <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
      {FEATURES.map((feat, i) => (
        <FeatureCard key={feat.title} feat={feat} index={i} />
      ))}
    </div>

    <div className="text-center">
      <a
        href="/"
        className="inline-flex items-center gap-2 px-10 py-4 bg-[#00ff9f] text-[#0a0a0f] font-bold text-base rounded-xl
                   hover:bg-[#00ffb3] active:scale-95 shadow-[0_0_24px_#00ff9f55]
                   hover:shadow-[0_0_40px_#00ff9f88] transition-all duration-200"
      >
        ⚡ Try CodeTrace Now
      </a>
    </div>
  </div>
);

export default Features;
