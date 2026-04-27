import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, AlertCircle, History as HistoryIcon, ArrowRight, Activity, ShieldAlert, CheckCircle2, Trash2 } from 'lucide-react';
import api from '../api/index';

const History = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isClearingAll, setIsClearingAll] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await api.get('/api/history');

        const sorted = response.data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        setHistory(sorted);
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load history.");
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  const handleClearAll = async () => {
    if (!window.confirm("Are you sure you want to clear all history? This cannot be undone.")) return;
    setIsClearingAll(true);
    try {
      await api.delete('/api/history/all');
      setHistory([]);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to clear history.");
    } finally {
      setIsClearingAll(false);
    }
  };

  const handleDeleteRow = async (id) => {
    if (!window.confirm("Are you sure you want to delete this record?")) return;
    setDeletingId(id);
    try {
      await api.delete(`/api/history/${id}`);
      setHistory(history.filter(item => item.id !== id));
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete record.");
    } finally {
      setDeletingId(null);
    }
  };

  const totalCount = history.length;
  const plagiarizedCount = history.filter(item => item.verdict.includes("Plagiarized") && !item.verdict.includes("Possibly")).length;
  const possiblyCount = history.filter(item => item.verdict.includes("Possibly")).length;
  const notPlagiarizedCount = history.filter(item => item.verdict.includes("Not")).length;

  const getScoreColor = (score) => {
    if (score < 30) return "#00ff9f";
    if (score <= 70) return "#fbbf24";
    return "#ef4444";
  };

  const getVerdictStyle = (verdict) => {
    if (verdict?.includes("Not")) return "text-[#00ff9f] border-[#00ff9f]/30 bg-[#00ff9f]/10";
    if (verdict?.includes("Possibly")) return "text-[#fbbf24] border-[#fbbf24]/30 bg-[#fbbf24]/10";
    if (verdict?.includes("Plagiarized")) return "text-[#ef4444] border-[#ef4444]/30 bg-[#ef4444]/10";
    return "text-[#8888aa] border-[#8888aa]/30 bg-[#8888aa]/10";
  };

  const formatDate = (dateString) => {
    const d = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(d);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white font-sans selection:bg-[#00ff9f]/30">
      
      
      <div className="pt-24 pb-12 px-6 flex flex-col items-center justify-center text-center">
        <h1 className="text-4xl font-semibold mb-4 tracking-tight text-white">Analysis History</h1>
        <p className="text-[#8888aa] text-lg font-light tracking-tight">Past plagiarism detection results</p>
      </div>

      <div className="max-w-7xl mx-auto px-6 pb-24">
        
        
        {loading && (
          <div className="flex flex-col items-center justify-center py-24 border border-[#1e1e2e] rounded-lg bg-[#0a0a0f]">
            <Loader2 size={32} className="animate-spin text-[#00ff9f] mb-4" />
            <p className="text-[#8888aa] text-sm">Fetching your history...</p>
          </div>
        )}

        
        {!loading && error && (
          <div className="p-4 rounded-md border border-[#ef4444]/30 bg-[#ef4444]/10 flex items-start gap-3 mb-8">
            <AlertCircle size={18} className="text-[#ef4444] mt-0.5" />
            <p className="text-sm text-[#ef4444]">{error}</p>
          </div>
        )}

        
        {!loading && !error && history.length > 0 && (
          <div className="animate-in fade-in duration-500 space-y-8">
            
            
            <div className="flex justify-end">
              <button
                onClick={handleClearAll}
                disabled={isClearingAll}
                className="flex items-center gap-2 px-4 py-2 bg-red-600/10 text-red-500 border border-red-600/30 rounded hover:bg-red-600/20 transition-colors disabled:opacity-50 text-sm font-medium"
              >
                {isClearingAll ? <Loader2 size={16} className="animate-spin" /> : <Trash2 size={16} />}
                Clear All History
              </button>
            </div>

            
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-6 border border-[#1e1e2e] rounded-lg bg-[#0a0a0f] flex flex-col hover:border-white/20 transition-colors">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs text-[#8888aa] uppercase tracking-widest font-medium">Total Runs</span>
                  <Activity size={16} className="text-[#8888aa]" />
                </div>
                <span className="text-3xl font-semibold text-white tracking-tight">{totalCount}</span>
              </div>
              <div className="p-6 border border-[#ef4444]/30 bg-[#ef4444]/5 rounded-lg flex flex-col hover:border-[#ef4444]/50 transition-colors">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs text-[#ef4444] uppercase tracking-widest font-medium">Plagiarized</span>
                  <ShieldAlert size={16} className="text-[#ef4444]" />
                </div>
                <span className="text-3xl font-semibold text-[#ef4444] tracking-tight">{plagiarizedCount}</span>
              </div>
              <div className="p-6 border border-[#fbbf24]/30 bg-[#fbbf24]/5 rounded-lg flex flex-col hover:border-[#fbbf24]/50 transition-colors">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs text-[#fbbf24] uppercase tracking-widest font-medium">Possibly Plagiarized</span>
                  <AlertCircle size={16} className="text-[#fbbf24]" />
                </div>
                <span className="text-3xl font-semibold text-[#fbbf24] tracking-tight">{possiblyCount}</span>
              </div>
              <div className="p-6 border border-[#00ff9f]/30 bg-[#00ff9f]/5 rounded-lg flex flex-col hover:border-[#00ff9f]/50 transition-colors">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs text-[#00ff9f] uppercase tracking-widest font-medium">Not Plagiarized</span>
                  <CheckCircle2 size={16} className="text-[#00ff9f]" />
                </div>
                <span className="text-3xl font-semibold text-[#00ff9f] tracking-tight">{notPlagiarizedCount}</span>
              </div>
            </div>

            
            <div className="border border-[#1e1e2e] rounded-lg overflow-hidden bg-[#0a0a0f]">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse whitespace-nowrap">
                  <thead>
                    <tr className="border-b border-[#1e1e2e] bg-[#12121a]/50">
                      <th className="px-6 py-4 text-xs font-medium text-[#8888aa] uppercase tracking-wider w-12 text-center">#</th>
                      <th className="px-6 py-4 text-xs font-medium text-[#8888aa] uppercase tracking-wider">File 1</th>
                      <th className="px-6 py-4 text-xs font-medium text-[#8888aa] uppercase tracking-wider">File 2</th>
                      <th className="px-6 py-4 text-xs font-medium text-[#8888aa] uppercase tracking-wider">Language</th>
                      <th className="px-6 py-4 text-xs font-medium text-[#8888aa] uppercase tracking-wider">Lexical</th>
                      <th className="px-6 py-4 text-xs font-medium text-[#8888aa] uppercase tracking-wider">Syntax</th>
                      <th className="px-6 py-4 text-xs font-medium text-[#8888aa] uppercase tracking-wider">Semantic</th>
                      <th className="px-6 py-4 text-xs font-medium text-[#8888aa] uppercase tracking-wider">CFG</th>
                      <th className="px-6 py-4 text-xs font-medium text-[#8888aa] uppercase tracking-wider">PDG</th>
                      <th className="px-6 py-4 text-xs font-medium text-white uppercase tracking-wider">Final</th>
                      <th className="px-6 py-4 text-xs font-medium text-[#8888aa] uppercase tracking-wider">Verdict</th>
                      <th className="px-6 py-4 text-xs font-medium text-[#8888aa] uppercase tracking-wider text-right">Date</th>
                      <th className="px-6 py-4"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1e1e2e]">
                    {history.map((item, idx) => (
                      <tr key={item.id} className="hover:bg-white/[0.02] transition-colors group">
                        <td className="px-6 py-4 text-sm text-[#555566] text-center">{idx + 1}</td>
                        <td className="px-6 py-4 text-sm font-mono text-white">
                          <div className="max-w-[150px] truncate" title={item.file1_name}>{item.file1_name}</div>
                        </td>
                        <td className="px-6 py-4 text-sm font-mono text-white">
                          <div className="max-w-[150px] truncate" title={item.file2_name}>{item.file2_name}</div>
                        </td>
                        <td className="px-6 py-4 text-sm text-[#8888aa] uppercase">{item.language}</td>
                        <td className="px-6 py-4 text-sm text-[#8888aa]">{Math.round(item.lexical_score)}%</td>
                        <td className="px-6 py-4 text-sm text-[#8888aa]">{Math.round(item.syntax_score)}%</td>
                        <td className="px-6 py-4 text-sm text-[#8888aa]">{Math.round(item.semantic_score)}%</td>
                        <td className="px-6 py-4 text-sm text-[#8888aa]">{Math.round(item.cfg_score)}%</td>
                        <td className="px-6 py-4 text-sm text-[#8888aa]">{Math.round(item.pdg_score)}%</td>
                        <td className="px-6 py-4 text-sm font-semibold" style={{ color: getScoreColor(item.final_score) }}>
                          {Math.round(item.final_score)}%
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium border uppercase tracking-wide ${getVerdictStyle(item.verdict)}`}>
                            {item.verdict}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-[#8888aa] text-right">
                          {formatDate(item.created_at)}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button
                            onClick={() => handleDeleteRow(item.id)}
                            disabled={deletingId === item.id}
                            className="p-1.5 text-red-500/70 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors disabled:opacity-50"
                            title="Delete record"
                          >
                            {deletingId === item.id ? <Loader2 size={16} className="animate-spin" /> : <Trash2 size={16} />}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            
          </div>
        )}

        
        {!loading && !error && history.length === 0 && (
          <div className="flex flex-col items-center justify-center py-32 border border-[#1e1e2e] rounded-lg bg-[#0a0a0f] text-center px-6">
            <HistoryIcon size={48} className="text-[#333344] mb-6" />
            <h3 className="text-xl font-medium text-white mb-2">No analysis history yet.</h3>
            <p className="text-[#8888aa] max-w-md mb-8">Start by analyzing some code!</p>
            <button 
              onClick={() => navigate('/analyze')}
              className="group flex items-center gap-2 px-6 py-3 bg-[#00ff9f] text-black font-medium rounded-md hover:bg-[#00cc7f] transition-colors"
            >
              Start Analysis
              <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        )}

      </div>
    </div>
  );
};

export default History;
