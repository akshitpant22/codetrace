import React, { useState, useRef } from 'react';
import { Upload, FileCode2, Loader2, AlertCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import api from '../api/index';

const Analyze = () => {
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  const [language, setLanguage] = useState('python');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const file1Ref = useRef(null);
  const file2Ref = useRef(null);

  const handleFileChange = (e, setFile) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleDrop = (e, setFile) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const preventDefault = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleAnalyze = async () => {
    if (!file1 || !file2) {
      setError("Please select both files for analysis.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file1', file1);
    formData.append('file2', file2);
    formData.append('language', language);

    try {
      const response = await api.post('/api/analyze', formData);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred during analysis.");
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score < 30) return "#00ff9f";
    if (score <= 70) return "#fbbf24";
    return "#ef4444";
  };

  const getVerdictColor = (verdict) => {
    if (verdict?.includes("Not")) return "text-[#00ff9f] border-[#00ff9f]/30 bg-[#00ff9f]/10";
    if (verdict?.includes("Possibly")) return "text-[#fbbf24] border-[#fbbf24]/30 bg-[#fbbf24]/10";
    return "text-[#ef4444] border-[#ef4444]/30 bg-[#ef4444]/10";
  };

  const chartData = result ? [
    { name: 'Lexical', score: result.lexical_score },
    { name: 'Syntax', score: result.syntax_score },
    { name: 'Semantic', score: result.semantic_score },
    { name: 'CFG', score: result.cfg_score },
    { name: 'PDG', score: result.pdg_score },
  ] : [];

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white font-sans selection:bg-[#00ff9f]/30">
      
      
      <div className="pt-24 pb-12 px-6 flex flex-col items-center justify-center text-center">
        <h1 className="text-4xl font-semibold mb-4 tracking-tight text-white">Code Analysis</h1>
        <p className="text-[#8888aa] text-lg font-light tracking-tight">Compare two files for plagiarism</p>
      </div>

      <div className="max-w-4xl mx-auto px-6 pb-24">
        
        
        <div className="bg-[#0a0a0f] border border-[#1e1e2e] rounded-lg p-6 mb-8">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            
            <div 
              className={`border border-dashed rounded-lg p-8 flex flex-col items-center justify-center cursor-pointer transition-colors ${file1 ? 'border-[#00ff9f] bg-[#00ff9f]/5' : 'border-[#1e1e2e] hover:border-white/20 hover:bg-white/[0.02]'}`}
              onClick={() => file1Ref.current?.click()}
              onDragOver={preventDefault}
              onDrop={(e) => handleDrop(e, setFile1)}
            >
              <input type="file" ref={file1Ref} className="hidden" onChange={(e) => handleFileChange(e, setFile1)} />
              {file1 ? (
                <>
                  <FileCode2 size={24} className="text-[#00ff9f] mb-3" />
                  <span className="text-white font-medium text-sm text-center break-all">{file1.name}</span>
                </>
              ) : (
                <>
                  <Upload size={24} className="text-[#8888aa] mb-3" />
                  <span className="text-[#8888aa] text-sm font-medium">Upload File 1</span>
                  <span className="text-[#555566] text-xs mt-1">Drag & Drop or Click</span>
                </>
              )}
            </div>

            
            <div 
              className={`border border-dashed rounded-lg p-8 flex flex-col items-center justify-center cursor-pointer transition-colors ${file2 ? 'border-[#00ff9f] bg-[#00ff9f]/5' : 'border-[#1e1e2e] hover:border-white/20 hover:bg-white/[0.02]'}`}
              onClick={() => file2Ref.current?.click()}
              onDragOver={preventDefault}
              onDrop={(e) => handleDrop(e, setFile2)}
            >
              <input type="file" ref={file2Ref} className="hidden" onChange={(e) => handleFileChange(e, setFile2)} />
              {file2 ? (
                <>
                  <FileCode2 size={24} className="text-[#00ff9f] mb-3" />
                  <span className="text-white font-medium text-sm text-center break-all">{file2.name}</span>
                </>
              ) : (
                <>
                  <Upload size={24} className="text-[#8888aa] mb-3" />
                  <span className="text-[#8888aa] text-sm font-medium">Upload File 2</span>
                  <span className="text-[#555566] text-xs mt-1">Drag & Drop or Click</span>
                </>
              )}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-6 border-t border-[#1e1e2e]">
            <div className="w-full sm:w-auto flex items-center gap-4">
              <span className="text-sm font-medium text-[#8888aa]">Language:</span>
              <select 
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="bg-[#12121a] border border-[#1e1e2e] text-white text-sm rounded-md px-4 py-2 outline-none focus:border-[#00ff9f] transition-colors"
              >
                <option value="python">Python</option>
                <option value="c">C</option>
                <option value="cpp">C++</option>
                <option value="java">Java</option>
              </select>
            </div>
            
            <button 
              onClick={handleAnalyze}
              disabled={loading || !file1 || !file2}
              className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-2 bg-[#00ff9f] text-black font-medium rounded-md hover:bg-[#00e68f] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? <Loader2 size={18} className="animate-spin" /> : "Analyze"}
            </button>
          </div>
          
          
          {error && (
            <div className="mt-6 p-4 rounded-md border border-[#ef4444]/30 bg-[#ef4444]/10 flex items-start gap-3">
              <AlertCircle size={18} className="text-[#ef4444] mt-0.5" />
              <p className="text-sm text-[#ef4444]">{error}</p>
            </div>
          )}
        </div>

        
        {loading && (
          <div className="flex flex-col items-center justify-center py-24 border border-[#1e1e2e] rounded-lg">
            <Loader2 size={32} className="animate-spin text-[#00ff9f] mb-4" />
            <p className="text-[#8888aa] text-sm">Analyzing code...</p>
          </div>
        )}

        
        {result && !loading && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            
            <div className="md:col-span-1 border border-[#1e1e2e] rounded-lg p-8 flex flex-col items-center justify-center text-center">
              <h3 className="text-sm font-medium text-[#8888aa] mb-6 uppercase tracking-widest">Final Match</h3>
              
              <div className="text-7xl font-semibold mb-6 tracking-tighter" style={{ color: getScoreColor(result.final_score) }}>
                {Math.round(result.final_score)}%
              </div>
              
              <div className={`px-4 py-1.5 rounded-full border text-xs font-medium uppercase tracking-wider ${getVerdictColor(result.verdict)}`}>
                {result.verdict}
              </div>
            </div>

            
            <div className="md:col-span-2 border border-[#1e1e2e] rounded-lg p-8">
              <h3 className="text-sm font-medium text-[#8888aa] mb-8 uppercase tracking-widest">Analysis Breakdown</h3>
              
              <div className="mb-10">
                <div className="h-48 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#8888aa', fontSize: 12 }} dy={10} />
                      <YAxis axisLine={false} tickLine={false} tick={{ fill: '#8888aa', fontSize: 12 }} />
                      <Tooltip 
                        cursor={{ fill: 'transparent' }} 
                        contentStyle={{ backgroundColor: '#12121a', border: '1px solid #1e1e2e', borderRadius: '4px' }}
                        itemStyle={{ color: '#fff' }}
                      />
                      <Bar dataKey="score" radius={[2, 2, 0, 0]} maxBarSize={40}>
                        {chartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={getScoreColor(entry.score)} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="space-y-4">
                {chartData.map((item, i) => (
                  <div key={i} className="flex flex-col gap-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-[#8888aa]">{item.name}</span>
                      <span className="text-white font-medium">{Math.round(item.score)}%</span>
                    </div>
                    <div className="w-full bg-[#12121a] h-1.5 rounded-full overflow-hidden">
                      <div 
                        className="h-full rounded-full transition-all duration-1000 ease-out" 
                        style={{ width: `${item.score}%`, backgroundColor: getScoreColor(item.score) }}
                      />
                    </div>
                  </div>
                ))}
              </div>

            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default Analyze;
