import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  FileText, 
  Upload, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Sparkles, 
  ArrowRight, 
  History,
  Tag,
  Target,
  FileCheck
} from 'lucide-react';

const SAMPLE_DEMO_RESUME = `Alex Mercer
alex.mercer@example.com | github.com/alexmercer | linkedin.com/in/alexmercer
B.Tech in Computer Science and Engineering, CGPA: 8.8/10.0 (Graduating 2026)

TECHNICAL SKILLS:
- Languages: Python, Java, C++, JavaScript, SQL
- Frameworks & Web: React.js, FastAPI, Node.js, RESTful APIs, WebSockets
- Tools & Systems: Git, Docker, SQLite, PostgreSQL, Linux, Unit Testing (pytest)
- Core CS: Data Structures, Algorithms, DBMS, Operating Systems, OOP, Distributed Systems

PROJECTS:
1. Collaborative Real-Time Code Editor (React, WebSockets, Python, Docker)
- Architected a real-time collaborative code editor supporting 50+ concurrent users with sub-25ms sync latency.
- Implemented operational transformation algorithms ensuring zero-conflict collaborative code updates.
- Containerized microservices using Docker for streamlined multi-environment deployment.

2. In-Memory Distributed Caching Engine (Python, Data Structures)
- Designed an in-memory key-value cache implementing LRU (Least Recently Used) eviction policy via doubly linked lists and hash maps.
- Optimized average lookup and write latency to sub-2ms across 100,000 cached records.

WORK EXPERIENCE:
Software Engineering Intern | TechCorp (Summer 2025)
- Automated API regression testing suite using pytest and GitHub Actions, cutting release test cycles by 35%.
- Refactored backend SQL queries and added compound indexes, improving query throughput by 42%.`;

export default function ResumeAnalyzerPage() {
  const [targetRole, setTargetRole] = useState('Software Development Engineer (SDE)');
  const [resumeText, setResumeText] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const hist = await api.getResumeHistory();
      setHistory(hist || []);
      if (hist && hist.length > 0 && !analysisResult) {
        setAnalysisResult(hist[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleAnalyzeText = async (e) => {
    if (e) e.preventDefault();
    if (!resumeText.trim()) return;
    setAnalyzing(true);
    try {
      const res = await api.analyzeResumeText(resumeText, targetRole, 'Pasted_Resume.txt');
      setAnalysisResult(res);
      loadHistory();
    } catch (err) {
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('target_role', targetRole);

      const res = await api.uploadResumeFile(formData);
      setAnalysisResult(res);
      loadHistory();
    } catch (err) {
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleLoadDemoResume = () => {
    setResumeText(SAMPLE_DEMO_RESUME);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="p-6 rounded-2xl glass-card flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <FileText className="w-4 h-4" /> Agent 5: Resume Analysis Engine
          </div>
          <h2 className="text-xl font-bold text-white">ATS Quality & Keyword Gap Evaluator</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Audit your resume against technical role benchmarks. Detects missing keywords, evaluates structural formatting, flags skill gaps, and recommends high-impact bullet refinements.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-xs text-slate-400">Target Role:</label>
          <select
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="Software Development Engineer (SDE)">Software Development Engineer (SDE)</option>
            <option value="Frontend Developer">Frontend Developer</option>
            <option value="Backend Developer">Backend Developer</option>
            <option value="Data Scientist / ML Engineer">Data Scientist / ML Engineer</option>
          </select>
        </div>
      </div>

      {/* Upload / Paste Area */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Input Form (5 cols) */}
        <div className="lg:col-span-5 p-6 rounded-2xl glass-card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Submit Resume for Audit
            </h3>

            {/* Demo Accelerator Button */}
            <button
              type="button"
              onClick={handleLoadDemoResume}
              className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-indigo-950/80 hover:bg-indigo-900 border border-indigo-500/30 text-indigo-300 text-[11px] font-medium transition"
              title="Loads candidate resume template for instant demo presentation"
            >
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              Load Sample SDE Resume (Demo)
            </button>
          </div>

          {/* File Upload Box */}
          <div className="border-2 border-dashed border-slate-800 hover:border-indigo-500/50 rounded-xl p-5 text-center transition bg-slate-950/40 relative">
            <Upload className="w-6 h-6 text-indigo-400 mx-auto mb-2" />
            <span className="text-xs text-slate-300 font-semibold block">Upload PDF or Text File</span>
            <span className="text-[11px] text-slate-500 block mt-0.5">Click or drag your resume here</span>
            <input
              type="file"
              accept=".pdf,.txt,.doc,.docx"
              onChange={handleFileUpload}
              className="absolute inset-0 opacity-0 cursor-pointer"
            />
          </div>

          <div className="flex items-center gap-3 text-xs text-slate-400">
            <div className="flex-1 h-px bg-slate-800" />
            <span>OR PASTE TEXT</span>
            <div className="flex-1 h-px bg-slate-800" />
          </div>

          <form onSubmit={handleAnalyzeText} className="space-y-3">
            <textarea
              rows={8}
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste your education, skills, projects, and work experience here..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono leading-relaxed"
            />

            <button
              type="submit"
              disabled={analyzing || !resumeText.trim()}
              className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/25 transition disabled:opacity-40 flex items-center justify-center gap-2"
            >
              <Sparkles className="w-3.5 h-3.5" />
              {analyzing ? 'Agent 5 Parsing Resume...' : 'Analyze Resume Text'}
            </button>
          </form>
        </div>

        {/* Right: Analysis Report (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          {analysisResult ? (
            <div className="p-6 rounded-2xl glass-card space-y-6">
              {/* Score Overview */}
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div>
                  <span className="text-[10px] font-mono text-indigo-400 uppercase">Analysis Results</span>
                  <h3 className="text-base font-bold text-white mt-0.5">
                    ATS Match: {analysisResult.target_role}
                  </h3>
                </div>

                <div className="text-right">
                  <span className="text-3xl font-extrabold text-white">
                    {analysisResult.overall_score}%
                  </span>
                  <span className="text-[10px] text-slate-400 block font-semibold">Overall ATS Score</span>
                </div>
              </div>

              {/* Sub-Scores */}
              <div className="grid grid-cols-3 gap-3 text-center text-xs">
                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                  <span className="text-slate-400 text-[11px] block">Structure</span>
                  <span className="text-base font-bold text-white mt-1 block">
                    {analysisResult.structure_score}%
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                  <span className="text-slate-400 text-[11px] block">Keywords Match</span>
                  <span className="text-base font-bold text-white mt-1 block">
                    {analysisResult.keyword_score}%
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                  <span className="text-slate-400 text-[11px] block">Role Relevance</span>
                  <span className="text-base font-bold text-white mt-1 block">
                    {analysisResult.relevance_score}%
                  </span>
                </div>
              </div>

              {/* Keywords Match & Missing */}
              <div className="space-y-3">
                <div>
                  <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5 mb-2">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Matched Benchmark Keywords
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {analysisResult.matched_keywords?.map((kw, i) => (
                      <span key={i} className="text-[11px] px-2.5 py-0.5 rounded-md bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-mono">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <span className="text-xs font-bold text-rose-400 flex items-center gap-1.5 mb-2">
                    <XCircle className="w-3.5 h-3.5" /> Missing High-Priority Keywords
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {analysisResult.missing_keywords?.map((kw, i) => (
                      <span key={i} className="text-[11px] px-2.5 py-0.5 rounded-md bg-rose-500/10 text-rose-300 border border-rose-500/20 font-mono">
                        + {kw}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Skill Gaps */}
              {analysisResult.skill_gaps && analysisResult.skill_gaps.length > 0 && (
                <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30 text-xs space-y-2">
                  <span className="font-bold text-amber-300 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5" /> Identified Experience & Skill Gaps
                  </span>
                  <ul className="list-disc list-inside text-slate-300 space-y-1 pl-1">
                    {analysisResult.skill_gaps.map((gap, i) => (
                      <li key={i} className="leading-relaxed">{gap}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Actionable Suggestions */}
              {analysisResult.suggestions && analysisResult.suggestions.length > 0 && (
                <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-500/30 text-xs space-y-2">
                  <span className="font-bold text-indigo-300 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5" /> High-Impact Bullet Refinements
                  </span>
                  <ul className="list-disc list-inside text-slate-300 space-y-1 pl-1">
                    {analysisResult.suggestions.map((sug, i) => (
                      <li key={i} className="leading-relaxed">{sug}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="p-12 text-center text-slate-400 glass-card rounded-2xl">
              Paste or upload a resume to see full ATS evaluation and keyword gap breakdown.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
