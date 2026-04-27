import React, { useState, useRef, useEffect } from 'react';
import { Upload, FileCode2, Loader2, AlertCircle, X, ShieldAlert, CheckCircle2, ChevronRight } from 'lucide-react';
import api from '../api/index';

const MultiAnalyze = () => {
  const [files, setFiles] = useState([]);
  const [language, setLanguage] = useState('python');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const fileRef = useRef(null);
  const resultsRef = useRef(null);

  useEffect(() => {
    if (result && resultsRef.current) {
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    }
  }, [result]);
  const handleFileChange = (e) => {
    if (e.target.files) {
      addFiles(Array.from(e.target.files));
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      addFiles(Array.from(e.dataTransfer.files));
    }
  };

  const addFiles = (newFiles) => {
    setFiles(prev => {
      const combined = [...prev, ...newFiles];

      const unique = combined.filter((v, i, a) => a.findIndex(t => t.name === v.name) === i);
      if (unique.length > 10) {
        setError("Maximum 10 files allowed. Extra files were discarded.");
        return unique.slice(0, 10);
      }
      setError(null);
      return unique;
    });
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
    setError(null);
  };

  const preventDefault = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleAnalyze = async () => {
    if (files.length < 2) {
      setError("Please select at least 2 files for batch analysis.");
      return;
    }
    if (files.length > 10) {
      setError("Maximum 10 files allowed.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    formData.append('language', language);

    try {
      const response = await api.post('/api/multi-analyze', formData);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred during multi-file analysis.");
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score < 30) return "#00ff9f";
    if (score <= 70) return "#fbbf24";
    return "#ef4444";
  };

  const getVerdictStyle = (verdict) => {
    if (verdict?.includes("Not")) return "text-[#00ff9f] border-[#00ff9f]/30 bg-[#00ff9f]/10";
    if (verdict?.includes("Possibly")) return "text-[#fbbf24] border-[#fbbf24]/30 bg-[#fbbf24]/10";
    return "text-[#ef4444] border-[#ef4444]/30 bg-[#ef4444]/10";
  };

  const pairCount = (files.length * (files.length - 1)) / 2;

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white font-sans selection:bg-[#00ff9f]/30">
      
      
      <div className="pt-24 pb-12 px-6 flex flex-col items-center justify-center text-center">
        <h1 className="text-4xl font-semibold mb-4 tracking-tight text-white">Multi-File Analysis</h1>
        <p className="text-[#8888aa] text-lg font-light tracking-tight">Detect plagiarism across batch code repositories</p>
      </div>

      <div className="max-w-6xl mx-auto px-6 pb-24">
        
        
        <div className="bg-[#0a0a0f] border border-[#1e1e2e] rounded-lg p-6 mb-8">
          
          <div 
            className={`border border-dashed rounded-lg p-10 mb-6 flex flex-col items-center justify-center cursor-pointer transition-colors ${files.length > 0 ? 'border-[#1e1e2e]' : 'border-[#1e1e2e] hover:border-white/20 hover:bg-white/[0.02]'}`}
            onClick={() => { if(files.length === 0) fileRef.current?.click() }}
            onDragOver={preventDefault}
            onDrop={handleDrop}
          >
            <input type="file" multiple ref={fileRef} className="hidden" onChange={handleFileChange} />
            
            {files.length === 0 ? (
              <div className="flex flex-col items-center pointer-events-none">
                <Upload size={32} className="text-[#8888aa] mb-4" />
                <span className="text-[#8888aa] text-base font-medium mb-1">Upload Multiple Files</span>
                <span className="text-[#555566] text-sm">Drag & Drop or Click (2 to 10 files)</span>
              </div>
            ) : (
              <div className="w-full text-left cursor-default" onClick={e => e.stopPropagation()}>
                <div className="flex justify-between items-center mb-4">
                  <span className="text-sm font-medium text-[#8888aa]">{files.length} Files Staged</span>
                  <button 
                    onClick={() => fileRef.current?.click()}
                    className="text-xs text-[#00ff9f] hover:underline"
                  >
                    + Add More
                  </button>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                  {files.map((file, i) => (
                    <div key={i} className="flex items-center justify-between p-3 border border-[#1e1e2e] rounded bg-[#12121a]">
                      <div className="flex items-center gap-3 overflow-hidden">
                        <FileCode2 size={16} className="text-[#00ff9f] shrink-0" />
                        <span className="text-sm text-white truncate">{file.name}</span>
                      </div>
                      <button onClick={() => removeFile(i)} className="text-[#8888aa] hover:text-[#ef4444] transition-colors shrink-0">
                        <X size={16} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-[#1e1e2e]">
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
              disabled={loading || files.length < 2 || files.length > 10}
              className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-2 bg-[#00ff9f] text-black font-medium rounded-md hover:bg-[#00e68f] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? <Loader2 size={18} className="animate-spin" /> : "Analyze All Pairs"}
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
          <div className="flex flex-col items-center justify-center py-24 border border-[#1e1e2e] rounded-lg mb-8">
            <Loader2 size={32} className="animate-spin text-[#00ff9f] mb-4" />
            <p className="text-[#8888aa] text-sm">Analyzing {pairCount} file pair{pairCount !== 1 ? 's' : ''}...</p>
          </div>
        )}

        
        {result && !loading && (
          <div ref={resultsRef} className="space-y-8 animate-in fade-in duration-500">
            
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-6 border border-[#1e1e2e] rounded-lg bg-[#0a0a0f] flex flex-col">
                <span className="text-sm text-[#8888aa] mb-2 uppercase tracking-widest">Total Files</span>
                <span className="text-3xl font-semibold text-white tracking-tight">{result.session.total_files}</span>
              </div>
              <div className="p-6 border border-[#1e1e2e] rounded-lg bg-[#0a0a0f] flex flex-col">
                <span className="text-sm text-[#8888aa] mb-2 uppercase tracking-widest">Pairs Analyzed</span>
                <span className="text-3xl font-semibold text-white tracking-tight">{result.session.pair_results.length}</span>
              </div>
              <div className={`p-6 border rounded-lg flex flex-col ${result.suspicious_pairs.length > 0 ? 'border-[#ef4444]/30 bg-[#ef4444]/5' : 'border-[#00ff9f]/30 bg-[#00ff9f]/5'}`}>
                <span className={`text-sm mb-2 uppercase tracking-widest ${result.suspicious_pairs.length > 0 ? 'text-[#ef4444]' : 'text-[#00ff9f]'}`}>Suspicious Pairs</span>
                <span className={`text-3xl font-semibold tracking-tight ${result.suspicious_pairs.length > 0 ? 'text-[#ef4444]' : 'text-[#00ff9f]'}`}>
                  {result.suspicious_pairs.length}
                </span>
              </div>
            </div>

            
            {result.suspicious_pairs.length > 0 && (
              <div className="border border-[#ef4444]/30 rounded-lg overflow-hidden">
                <div className="bg-[#ef4444]/10 px-6 py-4 flex items-center gap-3 border-b border-[#ef4444]/30">
                  <ShieldAlert size={20} className="text-[#ef4444]" />
                  <h3 className="font-medium text-[#ef4444]">High Risk Detections</h3>
                </div>
                <div className="divide-y divide-[#1e1e2e] bg-[#0a0a0f]">
                  {result.suspicious_pairs.map((pair, idx) => (
                    <div key={idx} className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div className="flex items-center gap-3">
                        <span className="font-mono text-sm text-white">{pair.file1}</span>
                        <ChevronRight size={16} className="text-[#8888aa]" />
                        <span className="font-mono text-sm text-white">{pair.file2}</span>
                      </div>
                      <div className="flex items-center gap-6">
                        <div className="flex flex-col items-end">
                          <span className="text-xs text-[#8888aa] mb-1">Match Score</span>
                          <span className="font-semibold text-lg" style={{ color: getScoreColor(pair.final_score) }}>
                            {Math.round(pair.final_score)}%
                          </span>
                        </div>
                        <div className={`px-3 py-1 text-xs font-medium uppercase tracking-wide rounded border ${getVerdictStyle(pair.verdict)}`}>
                          {pair.verdict}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            
            <div className="border border-[#1e1e2e] rounded-lg overflow-hidden bg-[#0a0a0f]">
              <div className="px-6 py-5 border-b border-[#1e1e2e] flex items-center gap-3">
                <CheckCircle2 size={20} className="text-[#00ff9f]" />
                <h3 className="font-medium text-white">Full Similarity Matrix</h3>
              </div>
              
              {(() => {
                const uniqueFiles = Array.from(new Set(result.session.pair_results.flatMap(p => [p.file1_name, p.file2_name])));
                return (
                  <div className="overflow-x-auto p-6">
                    <table className="w-full text-center border-collapse">
                      <thead>
                        <tr>
                          <th className="p-3 border-b border-r border-[#1e1e2e]"></th>
                          {uniqueFiles.map(f => (
                            <th key={`col-${f}`} className="p-3 text-xs font-medium text-[#8888aa] truncate max-w-[100px] border-b border-[#1e1e2e]">{f}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {uniqueFiles.map(rowFile => (
                          <tr key={`row-${rowFile}`}>
                            <th className="p-3 text-xs font-medium text-[#8888aa] text-right truncate max-w-[150px] border-r border-[#1e1e2e]">{rowFile}</th>
                            {uniqueFiles.map(colFile => {
                              if (rowFile === colFile) {
                                return <td key={`cell-${rowFile}-${colFile}`} className="border border-[#1e1e2e] bg-[#12121a] text-[#8888aa] h-14 w-14 sm:h-16 sm:w-16">-</td>;
                              }
                              const pair = result.session.pair_results.find(
                                p => (p.file1_name === rowFile && p.file2_name === colFile) || (p.file1_name === colFile && p.file2_name === rowFile)
                              );
                              
                              if (!pair) return <td key={`empty-${rowFile}-${colFile}`} className="border border-[#1e1e2e] bg-[#0a0a0f] h-14 w-14 sm:h-16 sm:w-16"></td>;
                              
                              const score = Math.round(pair.final_score);
                              let bgClass = "bg-[#00ff9f]/20 text-[#00ff9f]";
                              if (score > 70) bgClass = "bg-[#ff4444]/20 text-[#ff4444]";
                              else if (score >= 30) bgClass = "bg-[#ffaa00]/20 text-[#ffaa00]";

                              return (
                                <td key={`data-${rowFile}-${colFile}`} className={`border border-[#1e1e2e] relative group cursor-pointer hover:brightness-125 transition-all h-14 w-14 sm:h-16 sm:w-16 ${bgClass}`}>
                                  <span className="font-mono text-sm">{score}%</span>
                                  
                                  <div className="absolute opacity-0 group-hover:opacity-100 transition-opacity z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-48 p-3 bg-[#12121a] border border-[#1e1e2e] rounded shadow-xl pointer-events-none text-left">
                                    <div className="flex justify-between items-center mb-2 pb-2 border-b border-[#1e1e2e]">
                                      <span className="text-white font-medium text-xs">Score Breakdown</span>
                                    </div>
                                    <div className="flex flex-col gap-1 text-xs text-white">
                                      <div className="flex justify-between"><span className="text-[#8888aa]">Lexical:</span><span>{Math.round(pair.lexical_score)}%</span></div>
                                      <div className="flex justify-between"><span className="text-[#8888aa]">Syntax:</span><span>{Math.round(pair.syntax_score)}%</span></div>
                                      <div className="flex justify-between"><span className="text-[#8888aa]">Semantic:</span><span>{Math.round(pair.semantic_score)}%</span></div>
                                      <div className="flex justify-between"><span className="text-[#8888aa]">CFG:</span><span>{Math.round(pair.cfg_score)}%</span></div>
                                      <div className="flex justify-between"><span className="text-[#8888aa]">PDG:</span><span>{Math.round(pair.pdg_score)}%</span></div>
                                    </div>
                                  </div>
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                );
              })()}
            </div>

          </div>
        )}

      </div>
    </div>
  );
};

export default MultiAnalyze;
