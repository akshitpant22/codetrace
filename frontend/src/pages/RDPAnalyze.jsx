import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Loader2, Upload } from 'lucide-react';
import { useAuth } from "../contexts/AuthContext";

const RDPAnalyze = () => {
  const [code1, setCode1] = useState('');
  const [code2, setCode2] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  
  const { user } = useAuth();
  const navigate = useNavigate();
  const resultsRef = useRef(null);

  useEffect(() => {
    if (user === null) {
      navigate('/login');
    }
  }, [user, navigate]);

  useEffect(() => {
    if (results && resultsRef.current) {
      setTimeout(() => {
        resultsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    }
  }, [results]);

  const handleFileUpload = (e, setCodeFunc) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (event) => {
      setCodeFunc(event.target.result);
    };
    reader.readAsText(file);
  };

  const handleAnalyze = async () => {
    if (!code1.trim() || !code2.trim()) {
      setError('Please provide code in both editors.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:8000/api/rdp-analyze', {
        code1,
        code2
      });
      setResults(response.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'An error occurred while analyzing the code.');
    } finally {
      setLoading(false);
    }
  };

  const renderHighlightedSequence = (seq, otherSeq) => {
    return seq.map((node, i) => {

      const isMatch = otherSeq[i] === node;
      return (
        <span 
          key={i} 
          className={`inline-block px-1.5 py-0.5 m-0.5 rounded text-xs font-mono ${isMatch ? 'bg-[#00ff9f]/20 text-[#00ff9f]' : 'bg-[#1e1e2e] text-[#8888aa]'}`}
        >
          {node}
        </span>
      );
    });
  };

  const extractSequence = (tree) => {
    const seq = [];
    if (!tree || !tree.type) return seq;
    seq.push(tree.type);
    
    if (Array.isArray(tree.body)) {
      tree.body.forEach(child => seq.push(...extractSequence(child)));
    }
    if (Array.isArray(tree.else_body)) {
      tree.else_body.forEach(child => seq.push(...extractSequence(child)));
    }
    return seq;
  };

  let seq1 = [];
  let seq2 = [];
  if (results) {
    seq1 = extractSequence(results.parse_tree1);
    seq2 = extractSequence(results.parse_tree2);
  }

  const getVerdictBadgeColor = (verdict) => {
    if (verdict === "Not Plagiarized") return "bg-green-900 text-green-300 border-green-800";
    if (verdict === "Possibly Plagiarized") return "bg-yellow-900 text-yellow-300 border-yellow-800";
    return "bg-red-900 text-red-300 border-red-800";
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white p-8 pb-20">
      <div className="max-w-7xl mx-auto space-y-8">
        
        
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-white">RDP Parser Analyzer</h1>
          <p className="text-[#8888aa]">Custom Recursive Descent Parser — Compiler Design</p>
        </div>

        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-sm font-semibold text-[#8888aa] uppercase tracking-wider">Code 1</label>
              <label className="cursor-pointer flex items-center gap-2 px-3 py-1.5 text-xs font-semibold text-[#8888aa] border border-[#1e1e2e] bg-[#12121a] hover:border-[#8888aa] hover:text-white transition-colors rounded">
                <Upload className="w-3 h-3" />
                Upload .py
                <input type="file" accept=".py" className="hidden" onChange={(e) => handleFileUpload(e, setCode1)} />
              </label>
            </div>
            <textarea
              className="w-full h-80 bg-[#12121a] border border-[#1e1e2e] rounded-lg p-4 font-mono text-sm text-[#ffffff] focus:outline-none focus:border-green-900 transition-colors resize-none leading-relaxed"
              value={code1}
              onChange={(e) => setCode1(e.target.value)}
              placeholder="Paste Python code here..."
              spellCheck={false}
            />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-sm font-semibold text-[#8888aa] uppercase tracking-wider">Code 2</label>
              <label className="cursor-pointer flex items-center gap-2 px-3 py-1.5 text-xs font-semibold text-[#8888aa] border border-[#1e1e2e] bg-[#12121a] hover:border-[#8888aa] hover:text-white transition-colors rounded">
                <Upload className="w-3 h-3" />
                Upload .py
                <input type="file" accept=".py" className="hidden" onChange={(e) => handleFileUpload(e, setCode2)} />
              </label>
            </div>
            <textarea
              className="w-full h-80 bg-[#12121a] border border-[#1e1e2e] rounded-lg p-4 font-mono text-sm text-[#ffffff] focus:outline-none focus:border-green-900 transition-colors resize-none leading-relaxed"
              value={code2}
              onChange={(e) => setCode2(e.target.value)}
              placeholder="Paste Python code to compare against..."
              spellCheck={false}
            />
          </div>
        </div>

        {error && <p className="text-red-400 text-center text-sm">{error}</p>}

        
        <div className="flex justify-center">
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full md:w-1/2 bg-[#00ff9f] hover:bg-[#00cc7f] text-black font-bold tracking-wide uppercase py-4 rounded-lg transition-colors flex items-center justify-center disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : "Parse & Compare"}
          </button>
        </div>

        
        {results && (
          <>
            <hr className="border-[#1e1e2e] my-12" />
            <div ref={resultsRef} className="bg-[#12121a] border border-[#1e1e2e] rounded-xl p-8 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            
            <div className="flex flex-col items-center justify-center space-y-4">
              <div className="text-7xl font-black text-[#00ff9f] drop-shadow-[0_0_15px_rgba(0,255,159,0.3)]">
                {results.similarity_score.toFixed(2)}%
              </div>
              <div className={`px-6 py-2 rounded-full border text-sm font-bold uppercase tracking-widest ${getVerdictBadgeColor(results.verdict)}`}>
                {results.verdict}
              </div>
            </div>

            
            <div className="space-y-4 pt-6 border-t border-[#1e1e2e]">
              <h3 className="text-sm font-semibold text-[#8888aa] uppercase tracking-wider">
                Structural Node Sequence
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-[#0a0a0f] p-4 rounded-lg border border-[#1e1e2e] break-words">
                  {renderHighlightedSequence(seq1, seq2)}
                </div>
                <div className="bg-[#0a0a0f] p-4 rounded-lg border border-[#1e1e2e] break-words">
                  {renderHighlightedSequence(seq2, seq1)}
                </div>
              </div>
            </div>

            
            <div className="space-y-4 pt-6 border-t border-[#1e1e2e]">
              <h3 className="text-sm font-semibold text-[#8888aa] uppercase tracking-wider">
                Generated Parse Trees (JSON)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <pre className="bg-[#0d0d14] p-4 rounded-lg border border-[#1e1e2e] overflow-y-auto max-h-[400px] text-xs text-[#a0a0b0] font-mono scrollbar-thin scrollbar-thumb-[#1e1e2e] scrollbar-track-transparent">
                  {JSON.stringify(results.parse_tree1, null, 2)}
                </pre>
                <pre className="bg-[#0d0d14] p-4 rounded-lg border border-[#1e1e2e] overflow-y-auto max-h-[400px] text-xs text-[#a0a0b0] font-mono scrollbar-thin scrollbar-thumb-[#1e1e2e] scrollbar-track-transparent">
                  {JSON.stringify(results.parse_tree2, null, 2)}
                </pre>
              </div>
            </div>

          </div>
          </>
        )}

      </div>
    </div>
  );
};

export default RDPAnalyze;
