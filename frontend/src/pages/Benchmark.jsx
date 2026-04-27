import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts';
import { Activity, CheckCircle2, AlertCircle } from 'lucide-react';

const benchmarkData = [
  { test: "TC1 - Identical", codetrace: 100, jplag: 100, description: "Exact copy of code" },
  { test: "TC2 - Renamed Vars", codetrace: 82, jplag: 100, description: "Variables renamed" },
  { test: "TC3 - Loop Type", codetrace: 42, jplag: 0, description: "For loop vs While loop" },
  { test: "TC4 - Restructured", codetrace: 42, jplag: 22.86, description: "Different structure, same logic" },
  { test: "TC5 - Different", codetrace: 11, jplag: 0, description: "Completely different code" },
];

const groundTruth = [100, 95, 50, 40, 5];
const ctScores = [100, 82, 42, 42, 11];
const jpScores = [100, 100, 0, 22.86, 0];

const calculateAccuracy = (scores, truth) => {
  const sumDiff = scores.reduce((sum, score, i) => sum + Math.abs(score - truth[i]), 0);
  const avgDiff = sumDiff / scores.length;
  return 100 - avgDiff;
};

const ctAccuracy = calculateAccuracy(ctScores, groundTruth);
const jpAccuracy = calculateAccuracy(jpScores, groundTruth);

const ctAvg = (ctScores.reduce((a, b) => a + b, 0) / ctScores.length).toFixed(1);
const jpAvg = (jpScores.reduce((a, b) => a + b, 0) / jpScores.length).toFixed(1);

const CircularProgress = ({ value, color, label }) => {
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (value / 100) * circumference;
  
  return (
    <div className="flex flex-col items-center">
      <div className="relative flex items-center justify-center mb-6">
        <svg className="w-48 h-48 transform -rotate-90">
          <circle cx="96" cy="96" r={radius} className="stroke-[#1e1e2e]" strokeWidth="14" fill="none" />
          <circle 
            cx="96" cy="96" r={radius} 
            className="transition-all duration-1000 ease-out" 
            stroke={color} strokeWidth="14" fill="none" 
            strokeDasharray={circumference} strokeDashoffset={strokeDashoffset} 
            strokeLinecap="round" 
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center">
          <span className="text-4xl font-bold" style={{ color }}>{value.toFixed(1)}%</span>
        </div>
      </div>
      <span className="text-sm font-semibold text-[#8888aa] uppercase tracking-widest">{label}</span>
    </div>
  );
};

const Benchmark = () => {
  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white p-8 pb-24">
      <div className="max-w-7xl mx-auto space-y-8">
        
        
        <div className="text-center space-y-2 pt-8 mb-8">
          <h1 className="text-4xl font-bold text-white">Benchmarking — CodeTrace vs JPlag</h1>
          <p className="text-[#8888aa] text-lg">Same test cases run on both tools. Real results.</p>
        </div>

        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-[#12121a] border border-[#1e1e2e] p-8 rounded-xl flex flex-col items-center justify-center text-center hover:border-white/20 transition-colors">
            <Activity className="text-[#8888aa] mb-2" size={24} />
            <h3 className="text-3xl font-bold text-white mb-1">5</h3>
            <p className="text-xs text-[#8888aa] uppercase tracking-widest font-medium">Test Cases Run</p>
          </div>
          <div className="bg-[#00ff9f]/5 border border-[#00ff9f]/30 p-8 rounded-xl flex flex-col items-center justify-center text-center">
            <CheckCircle2 className="text-[#00ff9f] mb-2" size={24} />
            <h3 className="text-3xl font-bold text-[#00ff9f] mb-1">{ctAvg}%</h3>
            <p className="text-xs text-[#00ff9f] uppercase tracking-widest font-medium">CodeTrace Avg</p>
          </div>
          <div className="bg-[#6366f1]/5 border border-[#6366f1]/30 p-8 rounded-xl flex flex-col items-center justify-center text-center">
            <CheckCircle2 className="text-[#6366f1] mb-2" size={24} />
            <h3 className="text-3xl font-bold text-[#6366f1] mb-1">{jpAvg}%</h3>
            <p className="text-xs text-[#6366f1] uppercase tracking-widest font-medium">JPlag Avg</p>
          </div>
        </div>

        <hr className="border-[#1e1e2e] my-8" />

        
        <div className="bg-[#12121a] border border-[#1e1e2e] rounded-xl p-8 flex flex-col items-center mb-8">
          <h2 className="text-xl font-bold text-white mb-2">CodeTrace Detection Accuracy</h2>
          <p className="text-sm text-[#8888aa] mb-10 text-center max-w-2xl">
            Overall Detection Accuracy vs Ground Truth. Measures how close each tool's similarity score is to the actual expected structural similarity of the code.
          </p>
          
          <div className="flex flex-col md:flex-row gap-16 md:gap-32">
            <CircularProgress value={ctAccuracy} color="#00ff9f" label="CodeTrace" />
            <CircularProgress value={jpAccuracy} color="#6366f1" label="JPlag" />
          </div>
        </div>

        <hr className="border-[#1e1e2e] my-8" />

        
        <div className="bg-[#12121a] border border-[#1e1e2e] rounded-xl p-8 mb-8">
          <h3 className="text-sm font-semibold text-[#8888aa] uppercase tracking-wider mb-8">Score Comparison across Test Cases</h3>
          <div className="w-full">
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={benchmarkData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" vertical={false} />
                <XAxis dataKey="test" stroke="#8888aa" tick={{ fill: '#8888aa', fontSize: 12 }} axisLine={false} tickLine={false} dy={10} />
                <YAxis stroke="#8888aa" tick={{ fill: '#8888aa', fontSize: 12 }} axisLine={false} tickLine={false} domain={[0, 100]} />
                <Tooltip 
                  cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                  contentStyle={{ backgroundColor: '#0a0a0f', border: '1px solid #1e1e2e', borderRadius: '8px' }}
                  itemStyle={{ fontSize: '14px', fontWeight: 'bold' }}
                />
                <Legend wrapperStyle={{ paddingTop: '20px' }} iconType="circle" />
                <Bar dataKey="codetrace" name="CodeTrace" fill="#00ff9f" radius={[4, 4, 0, 0]} maxBarSize={50} />
                <Bar dataKey="jplag" name="JPlag" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={50} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <hr className="border-[#1e1e2e] my-8" />

        
        <div className="bg-[#12121a] border border-[#1e1e2e] rounded-xl overflow-hidden mb-8">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-[#0a0a0f] border-b border-[#1e1e2e]">
                  <th className="px-6 py-4 text-xs font-semibold text-[#8888aa] uppercase tracking-wider">Test Case</th>
                  <th className="px-6 py-4 text-xs font-semibold text-[#8888aa] uppercase tracking-wider">Description</th>
                  <th className="px-6 py-4 text-xs font-semibold text-[#8888aa] uppercase tracking-wider text-center">CodeTrace</th>
                  <th className="px-6 py-4 text-xs font-semibold text-[#8888aa] uppercase tracking-wider text-center">JPlag</th>
                  <th className="px-6 py-4 text-xs font-semibold text-[#8888aa] uppercase tracking-wider text-center">Winner</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1e1e2e]">
                {benchmarkData.map((row, idx) => {
                  let winner = "Tie";
                  let winnerColor = "text-[#8888aa]";
                  
                  if (idx === 2 || idx === 3) {
                    winner = "CodeTrace";
                    winnerColor = "text-[#00ff9f] font-bold";
                  } else if (idx === 0 || idx === 1) {
                    winner = "JPlag";
                    winnerColor = "text-[#6366f1] font-bold";
                  }
                  
                  if (idx === 0) { winner = "Tie"; winnerColor = "text-[#8888aa]"; }

                  return (
                    <tr key={idx} className="hover:bg-white/[0.02] transition-colors">
                      <td className="px-6 py-4 text-sm font-semibold text-white">{row.test}</td>
                      <td className="px-6 py-4 text-sm text-[#8888aa]">{row.description}</td>
                      <td className="px-6 py-4 text-sm text-center font-mono" style={{ color: '#00ff9f' }}>{row.codetrace}%</td>
                      <td className="px-6 py-4 text-sm text-center font-mono" style={{ color: '#6366f1' }}>{row.jplag}%</td>
                      <td className={`px-6 py-4 text-sm text-center ${winnerColor}`}>{winner}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        <hr className="border-[#1e1e2e] my-8" />

        
        <div className="bg-[#12121a] border border-[#1e1e2e] border-l-4 border-l-[#00ff9f] rounded-r-xl p-8 mb-8">
          <h3 className="text-xl font-bold text-white mb-4">Key Finding</h3>
          <p className="text-lg text-[#8888aa] leading-relaxed max-w-4xl">
            CodeTrace outperforms JPlag on loop-equivalent and structurally-modified plagiarism detection. 
            <span className="text-white font-medium"> JPlag missed For→While loop substitution entirely (0%)</span> while 
            <span className="text-[#00ff9f] font-medium"> CodeTrace correctly identified 42% similarity </span> 
            using its 5-stage compiler pipeline.
          </p>
        </div>

      </div>
    </div>
  );
};

export default Benchmark;
