import React, { useState, useEffect, useCallback, useRef } from "react";
import Editor from "@monaco-editor/react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell,
} from "recharts";
import api from "../api/index";

const LANGUAGES = [
  { label: "Python",     value: "python" },
  { label: "C",          value: "c"      },
  { label: "C++",        value: "cpp"    },
  { label: "Java",       value: "java"   },
  { label: "JavaScript", value: "js"     },
];

const SCORE_LABELS = [
  { key: "lexical_score",   label: "Lexical"   },
  { key: "syntax_score",    label: "Syntax"    },
  { key: "semantic_score",  label: "Semantic"  },
  { key: "final_score",     label: "Final"     },
];

const scoreColor = (score) => {
  if (score >= 70) return "#ff4d4d";
  if (score >= 30) return "#facc15";
  return "#00ff9f";
};

const ScoreRing = ({ score, active }) => {
  const [count, setCount] = useState(0);
  const color = scoreColor(score);
  const radius   = 68;
  const circ     = 2 * Math.PI * radius;
  const progress = circ - (count / 100) * circ;

  useEffect(() => {
    if (!active) { setCount(0); return; }
    let frame;
    const duration = 1200;
    const start = performance.now();
    const tick = (now) => {
      const t = Math.min((now - start) / duration, 1);
      setCount(score * (1 - Math.pow(1 - t, 3)));
      if (t < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [active, score]);

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative w-44 h-44">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 160 160">
          <circle cx="80" cy="80" r={radius} strokeWidth="10"
            stroke="#1e1e2e" fill="none" />
          <circle cx="80" cy="80" r={radius} strokeWidth="10"
            stroke={color} fill="none"
            strokeDasharray={circ}
            strokeDashoffset={progress}
            strokeLinecap="round"
            style={{
              transition: "stroke-dashoffset 0.05s linear",
              filter: `drop-shadow(0 0 8px ${color}88)`,
            }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="text-4xl font-extrabold leading-none"
            style={{ color, textShadow: `0 0 20px ${color}88` }}
          >
            {count.toFixed(1)}
          </span>
          <span className="text-lg font-bold" style={{ color }}>%</span>
        </div>
      </div>

      <p className="text-sm font-mono uppercase tracking-widest text-[#8888aa]">
        Final Plagiarism Score
      </p>
      <p className="font-semibold text-sm" style={{ color }}>
        {score >= 70 ? "🔴 High Plagiarism Detected"
          : score >= 30 ? "🟡 Moderate Similarity"
          : "🟢 Low Similarity"}
      </p>
    </div>
  );
};

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const val = payload[0].value;
  return (
    <div className="bg-[#12121a] border border-[#1e1e2e] rounded-xl px-4 py-3 text-sm
                     shadow-[0_8px_32px_#00000088]">
      <p className="text-[#8888aa] mb-1 font-mono text-xs uppercase tracking-widest">{label}</p>
      <p className="font-bold text-lg" style={{ color: scoreColor(val) }}>
        {val.toFixed(1)}%
      </p>
    </div>
  );
};

const EditorFrame = ({ slot, code, setCode, fileName, label, language, onUpload }) => {
  const [focused, setFocused] = useState(false);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <span className="w-3 h-3 rounded-full bg-[#ff5f57]" />
            <span className="w-3 h-3 rounded-full bg-[#febc2e]" />
            <span className="w-3 h-3 rounded-full bg-[#28c840]" />
          </div>
          <span className="text-[#8888aa] text-xs font-mono uppercase tracking-widest ml-2">
            {fileName ? `📄 ${fileName}` : label}
          </span>
        </div>
        <label className="cursor-pointer text-xs text-[#00ff9f] hover:underline transition font-medium">
          Upload File
          <input type="file" accept=".py,.c,.cpp,.java,.js" className="hidden" onChange={onUpload} />
        </label>
      </div>

      <div
        className="perspective-container"
        style={{
          transition: "transform 0.3s ease",
          transform: focused ? "perspective(1200px) rotateX(0deg)" : "perspective(1200px) rotateX(1.5deg)",
        }}
      >
        <div
          className="rounded-2xl overflow-hidden"
          style={{
            border: focused ? "1px solid #00ff9f55" : "1px solid #1e1e2e",
            boxShadow: focused
              ? "0 0 30px #00ff9f22, 0 24px 48px #00000088"
              : "0 12px 32px #00000066",
            transition: "all 0.3s ease",
            height: 400,
          }}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
        >
          <Editor
            height="100%"
            language={language}
            value={code}
            onChange={(val) => setCode(val || "")}
            theme="vs-dark"
            options={{
              fontSize: 13,
              fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              lineNumbers: "on",
              padding: { top: 14 },
              smoothScrolling: true,
              cursorBlinking: "phase",
              renderLineHighlight: "gutter",
            }}
          />
        </div>
      </div>
    </div>
  );
};

const Analyze = () => {
  const [language, setLanguage]   = useState("python");
  const [code1,    setCode1]      = useState("");
  const [code2,    setCode2]      = useState("");
  const [file1Name, setFile1Name] = useState(null);
  const [file2Name, setFile2Name] = useState(null);
  const [loading,  setLoading]    = useState(false);
  const [result,   setResult]     = useState(null);
  const [error,    setError]      = useState(null);
  const [revealed, setRevealed]   = useState(false);

  const resultsRef = useRef(null);

  useEffect(() => {
    if (result) {
      setRevealed(false);
      const t = setTimeout(() => {
        setRevealed(true);
        resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
      return () => clearTimeout(t);
    }
  }, [result]);

  const handleFileUpload = (slot) => (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      if (slot === 1) { setCode1(ev.target.result); setFile1Name(file.name); }
      else            { setCode2(ev.target.result); setFile2Name(file.name); }
    };
    reader.readAsText(file);
  };

  const handleAnalyze = useCallback(async () => {
    if (!code1.trim() || !code2.trim()) {
      setError("Both editors must contain code before analyzing.");
      return;
    }
    setError(null);
    setResult(null);
    setRevealed(false);
    setLoading(true);
    try {
      const ext = language === "cpp" ? ".cpp" : language === "java" ? ".java" : language === "c" ? ".c" : language === "js" ? ".js" : ".py";
      const form = new FormData();
      form.append("file1", new Blob([code1], { type: "text/plain" }), file1Name || `code1${ext}`);
      form.append("file2", new Blob([code2], { type: "text/plain" }), file2Name || `code2${ext}`);
      form.append("language", language);
      const { data } = await api.post("/api/analyze", form);
      setResult(data);
    } catch (err) {
      const detail = err.response?.data?.detail;
      const status = err.response?.status;
      if (detail) {
        setError(`Backend error (${status}): ${detail}`);
      } else if (err.code === "ERR_NETWORK" || !err.response) {
        setError("Cannot reach the backend. Make sure uvicorn is running on port 8000.");
      } else {
        setError(`Analysis failed (${status || "unknown error"}). Please try again.`);
      }
    } finally {
      setLoading(false);
    }
  }, [code1, code2, language, file1Name, file2Name]);

  const chartData = result
    ? SCORE_LABELS.map(({ key, label }) => ({ label, value: result[key] }))
    : [];

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-10 bg-[#10101a]">

      <div className="mb-10 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full
                         border border-[#00ff9f33] bg-[#00ff9f11] text-[#00ff9f]
                         text-xs font-mono tracking-widest uppercase mb-4 shadow-[0_0_20px_#00ff9f22]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#00ff9f] animate-pulse" />
          Code Plagiarism Detection
        </div>
        <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-4 tracking-tight">
          <span className="neon-green">CodeTrace</span>
        </h1>
        <p className="text-[#b0b0d0] text-lg max-w-2xl mx-auto mb-2">
          Advanced code plagiarism detection using lexical, syntax, and semantic analysis.<br/>
          Paste or upload two files, select a language, and run the 3-stage detection pipeline.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-4 mb-8
               bg-[#181828] border border-[#22224a] rounded-2xl px-6 py-5
               shadow-[0_4px_24px_#00000088] w-full max-w-3xl mx-auto">
        <div className="flex items-center gap-3">
          <label className="text-[#b0b0d0] text-xs font-mono uppercase tracking-widest">Language</label>
          <div className="flex gap-1">
            {LANGUAGES.map(({ label, value }) => (
              <button
                key={value}
                onClick={() => setLanguage(value)}
                className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all duration-150
                  ${language === value
                    ? "bg-[#00ff9f] text-[#181828] font-bold shadow-[0_0_14px_#00ff9f44]"
                    : "text-[#b0b0d0] hover:text-white hover:bg-white/5"
                  }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="ml-auto flex items-center gap-2 px-8 py-3
                     bg-[#00ff9f] text-[#181828] font-bold text-base rounded-xl
                     hover:bg-[#00ffb3] active:scale-95 disabled:opacity-50
                     shadow-[0_0_24px_#00ff9f55] hover:shadow-[0_0_40px_#00ff9f99]
                     transition-all duration-200"
          style={{ transform: "perspective(400px) translateZ(0)" }}
          onMouseEnter={(e) => !loading && (e.currentTarget.style.transform = "perspective(400px) translateZ(6px)")}
          onMouseLeave={(e) => (e.currentTarget.style.transform = "perspective(400px) translateZ(0)")}
        >
          {loading ? (
            <>
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
              </svg>
              Detecting…
            </>
          ) : (
            <>⚡ Detect</>
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10 w-full max-w-5xl mx-auto">
        <EditorFrame slot={1} code={code1} setCode={setCode1} fileName={file1Name}
          label="File 1" language={language} onUpload={handleFileUpload(1)} />
        <EditorFrame slot={2} code={code2} setCode={setCode2} fileName={file2Name}
          label="File 2" language={language} onUpload={handleFileUpload(2)} />
      </div>

      {error && (
        <div className="mb-8 px-6 py-4 rounded-2xl border border-red-500/30
                         bg-red-500/10 text-red-400 text-base font-semibold text-center
                         shadow-[0_0_20px_#ff444411] max-w-xl mx-auto">
          ⚠️ {error}
        </div>
      )}

      {result && (
        <div ref={resultsRef} className="grid grid-cols-1 md:grid-cols-2 gap-10 w-full max-w-5xl mx-auto">

          <div
            className="card-dark rounded-2xl p-8 flex flex-col items-center justify-center
                         border border-[#1e1e2e] score-pop"
            style={{ boxShadow: "0 0 40px #00000088" }}
          >
            <ScoreRing score={result.final_score} active={revealed} />

            <div className="mt-8 grid grid-cols-3 gap-3 w-full">
              {SCORE_LABELS.filter(s => s.key !== "final_score").map(({ key, label }, i) => (
                <div
                  key={key}
                  className="pill-rise text-center bg-[#0a0a0f] rounded-xl p-4
                               border border-[#1e1e2e] hover:border-[#00ff9f22]
                               hover:shadow-[0_0_12px_#00ff9f11] transition-all"
                  style={{ "--pill-delay": `${0.3 + i * 0.12}s` }}
                >
                  <p className="text-[#8888aa] text-xs mb-2 font-mono uppercase tracking-wider">{label}</p>
                  <p
                    className="font-bold text-base"
                    style={{ color: scoreColor(result[key]), textShadow: `0 0 10px ${scoreColor(result[key])}44` }}
                  >
                    {result[key].toFixed(1)}%
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div
            className="card-dark rounded-2xl p-7 border border-[#1e1e2e] score-pop"
            style={{ animationDelay: "0.1s", boxShadow: "0 0 40px #00000088" }}
          >
            <p className="text-white font-bold text-lg mb-2">Score Breakdown</p>
            <p className="text-[#8888aa] text-xs mb-6 font-mono">Comparative stage analysis</p>
            <div style={{ perspective: 600, perspectiveOrigin: "50% 100%" }}>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={chartData} barSize={44}>
                  <XAxis dataKey="label" tick={{ fill: "#8888aa", fontSize: 12 }}
                         axisLine={false} tickLine={false} />
                  <YAxis domain={[0, 100]} tick={{ fill: "#8888aa", fontSize: 11 }}
                         axisLine={false} tickLine={false} tickFormatter={(v) => `${v}%`} />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: "#ffffff06" }} />
                  <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                    {chartData.map((entry, i) => (
                      <Cell
                        key={i}
                        fill={scoreColor(entry.value)}
                        style={{ filter: `drop-shadow(0 0 10px ${scoreColor(entry.value)}99)` }}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Analyze;
