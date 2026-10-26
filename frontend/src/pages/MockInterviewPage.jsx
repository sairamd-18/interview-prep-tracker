import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  MessageSquareCode, 
  Send, 
  Bot, 
  Award, 
  CheckCircle2, 
  Sparkles, 
  ArrowRight, 
  RefreshCw,
  Clock,
  History,
  FileCode2,
  RotateCcw
} from 'lucide-react';

export default function MockInterviewPage() {
  const [interviewType, setInterviewType] = useState('Technical');
  const [targetRole, setTargetRole] = useState('Software Development Engineer (SDE)');
  const [activeInterview, setActiveInterview] = useState(null);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [candidateResponse, setCandidateResponse] = useState('');
  const [evaluating, setEvaluating] = useState(false);
  const [turnFeedback, setTurnFeedback] = useState(null);
  const [completedReport, setCompletedReport] = useState(null);
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const hist = await api.getInterviewHistory();
      setHistory(hist || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const startSession = async () => {
    setEvaluating(true);
    try {
      const data = await api.startInterview(interviewType, targetRole);
      setActiveInterview(data);
      setCurrentQIndex(0);
      setCandidateResponse('');
      setTurnFeedback(null);
      setCompletedReport(null);
    } catch (err) {
      console.error(err);
    } finally {
      setEvaluating(false);
    }
  };

  const handleSendResponse = async () => {
    if (!candidateResponse.trim() || !activeInterview) return;
    const currentQ = activeInterview.questions[currentQIndex];
    setEvaluating(true);

    try {
      const evalRes = await api.submitInterviewAnswer(
        activeInterview.interview_id,
        currentQ.id,
        candidateResponse
      );
      setTurnFeedback(evalRes);
    } catch (err) {
      console.error(err);
    } finally {
      setEvaluating(false);
    }
  };

  const handleNextQuestion = () => {
    setTurnFeedback(null);
    setCandidateResponse('');
    if (currentQIndex < activeInterview.questions.length - 1) {
      setCurrentQIndex(currentQIndex + 1);
    } else {
      finishInterview();
    }
  };

  const finishInterview = async () => {
    setEvaluating(true);
    try {
      const rep = await api.completeInterview(activeInterview.interview_id);
      setCompletedReport(rep);
      setActiveInterview(null);
      loadHistory();
    } catch (err) {
      console.error(err);
    } finally {
      setEvaluating(false);
    }
  };

  // Demo Accelerator: Populates a high-scoring sample response tailored to the question
  const handleFillDemoAnswer = () => {
    const currentQ = activeInterview?.questions[currentQIndex];
    if (!currentQ) return;
    const qText = (currentQ.question_text || '').toLowerCase();

    if (qText.includes('dynamic programming') || qText.includes('memoization')) {
      setCandidateResponse("Dynamic programming solves optimization problems by storing solutions to overlapping subproblems. Memoization is top-down recursion that caches results in memory, but incurs recursion call-stack overhead and risks stack overflows. Tabulation is bottom-up iteration that builds solutions iteratively in an array, allowing memory optimizations from O(N) to O(1) state variables. In production services, tabulation is preferred for predictable memory consumption and cache locality.");
    } else if (qText.includes('index') || qText.includes('b-tree')) {
      setCandidateResponse("B+ Tree database indexes keep keys sorted with leaf nodes linked sequentially in a doubly linked list. This enables O(log N) point searches and high-throughput range scans. However, creating unnecessary indexes introduces write amplification because every INSERT, UPDATE, and DELETE statement must update both the data table and the index structures, which strains disk I/O and buffer pool memory.");
    } else if (qText.includes('http') || qText.includes('browser') || qText.includes('tls') || qText.includes('url')) {
      setCandidateResponse("When requesting an HTTPS URL: 1. The browser performs DNS resolution to obtain the server's IP address. 2. A 3-way TCP handshake (SYN, SYN-ACK, ACK) establishes the connection. 3. The TLS handshake exchanges ClientHello/ServerHello, validates the SSL certificate via trusted Root CAs, and negotiates a symmetric session key using Diffie-Hellman. 4. Finally, an encrypted HTTP GET request is transmitted over the secure tunnel.");
    } else if (qText.includes('deadlock') || qText.includes('coffman')) {
      setCandidateResponse("Deadlocks require all four Coffman conditions: Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait. In production systems, we prevent deadlocks by enforcing a strict global lock hierarchy (breaking circular wait), utilizing try-lock with timeouts, or leveraging Dijkstra's Banker's algorithm to ensure the system never enters an unsafe resource allocation state.");
    } else if (qText.includes('coin change') || qText.includes('knapsack')) {
      setCandidateResponse("The Coin Change problem is an unbounded knapsack problem. We initialize a DP array of size amount + 1 with infinity, and set dp[0] = 0. For each coin denomination and each value from coin to amount, the recurrence relation is dp[i] = min(dp[i], 1 + dp[i - coin]). The time complexity is O(amount * n) where n is the number of coin types, and auxiliary space is O(amount).");
    } else if (qText.includes('star') || qText.includes('incident') || qText.includes('conflict') || qText.includes('project')) {
      setCandidateResponse("Situation: During our final semester platform rollout, API latency spiked to 2.4s under concurrent user traffic. Task: I needed to diagnose and resolve the bottleneck before placement evaluation. Action: I used query profiling to identify missing indexes and redundant N+1 ORM fetches. I refactored the SQL joins and added an in-memory Redis cache for frequently read session data. Result: Latency plummeted by 88% to under 120ms, and our automated stress tests maintained 100% success.");
    } else {
      setCandidateResponse("To address this systematically, I start by clarifying the functional and non-functional requirements. I analyze the trade-offs between time and space complexity, consider edge cases such as empty or out-of-bound inputs, and ensure test-driven coverage before deploying optimizations to production.");
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="p-6 rounded-2xl glass-card flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <MessageSquareCode className="w-4 h-4" /> Agent 4: Mock Interview Evaluation Engine
          </div>
          <h2 className="text-xl font-bold text-white">Interactive AI Interview Simulator</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Simulate technical & behavioral interview rounds. Evaluates answers across 5 metrics: Technical Correctness, Clarity, Confidence, Communication, and Relevance.
          </p>
        </div>

        {!activeInterview && (
          <div className="flex flex-wrap items-center gap-2">
            <select
              value={interviewType}
              onChange={(e) => setInterviewType(e.target.value)}
              className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="Technical">Technical Round</option>
              <option value="Behavioral">Behavioral (STAR) Round</option>
              <option value="Mixed">Comprehensive Mixed</option>
            </select>

            <button
              onClick={startSession}
              disabled={evaluating}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition transform active:scale-95 disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              {evaluating ? 'Generating Dynamic Questions...' : 'Start New Simulation'}
            </button>
          </div>
        )}
      </div>

      {/* Active Conversational Interview Stage */}
      {activeInterview && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-indigo-500/30 shadow-2xl space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800 text-xs">
            <div className="flex items-center gap-2">
              <span className="font-bold text-indigo-300">{activeInterview.interview_type} Session</span>
              <span>•</span>
              <span className="text-slate-400">Target: {activeInterview.target_role}</span>
            </div>
            <span className="font-mono text-purple-400 bg-purple-500/10 px-2.5 py-0.5 rounded-full border border-purple-500/20 font-bold">
              Question {currentQIndex + 1} of {activeInterview.questions.length}
            </span>
          </div>

          {/* Interviewer Message Bubble */}
          <div className="flex items-start gap-3 max-w-3xl">
            <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center text-white shrink-0 shadow-md">
              <Bot className="w-5 h-5" />
            </div>
            <div className="bg-slate-800/90 border border-slate-700/80 p-4 rounded-2xl rounded-tl-sm text-xs sm:text-sm text-slate-100 leading-relaxed shadow-lg">
              <div className="text-[10px] font-mono text-indigo-400 mb-1 font-semibold">
                Category: {activeInterview.questions[currentQIndex]?.category}
              </div>
              {activeInterview.questions[currentQIndex]?.question_text}
            </div>
          </div>

          {/* Candidate Response Area */}
          {!turnFeedback ? (
            <div className="space-y-3 pt-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Your Answer:</span>
                <div className="flex items-center gap-3">
                  <span>{candidateResponse.split(/\s+/).filter(Boolean).length} words</span>
                  
                  {/* Demo Helper Button */}
                  <button
                    type="button"
                    onClick={handleFillDemoAnswer}
                    className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-indigo-950/80 hover:bg-indigo-900 border border-indigo-500/30 text-indigo-300 text-[11px] font-medium transition"
                    title="Populates an optimal answer for immediate presentation"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                    Fill Sample Model Answer (Demo)
                  </button>
                </div>
              </div>

              <textarea
                rows={5}
                value={candidateResponse}
                onChange={(e) => setCandidateResponse(e.target.value)}
                placeholder="Explain the concept clearly, mention edge cases, and describe trade-offs..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 transition leading-relaxed"
              />

              <div className="flex justify-between items-center">
                <button
                  type="button"
                  onClick={() => setActiveInterview(null)}
                  className="text-xs text-slate-400 hover:text-white"
                >
                  Cancel Interview
                </button>

                <button
                  onClick={handleSendResponse}
                  disabled={evaluating || !candidateResponse.trim()}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition disabled:opacity-40"
                >
                  <Send className="w-3.5 h-3.5" />
                  {evaluating ? 'Agent 4 Evaluating Answer...' : 'Submit Response'}
                </button>
              </div>
            </div>
          ) : (
            /* Real-Time Turn Evaluation Card */
            <div className="p-5 rounded-2xl bg-indigo-950/20 border border-indigo-500/30 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Award className="w-4 h-4 text-indigo-400" />
                  <span className="text-xs font-bold text-white uppercase tracking-wider">
                    Agent 4 Turn Scorecard
                  </span>
                </div>
                <div className="text-sm font-extrabold text-indigo-300">
                  Overall: {turnFeedback.overall_score}/100
                </div>
              </div>

              {/* 5 Dimensions Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-center text-xs">
                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Technical</span>
                  <span className="font-bold text-white text-sm">{turnFeedback.technical_score}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Clarity</span>
                  <span className="font-bold text-white text-sm">{turnFeedback.clarity_score}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Confidence</span>
                  <span className="font-bold text-white text-sm">{turnFeedback.confidence_score}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Communication</span>
                  <span className="font-bold text-white text-sm">{turnFeedback.communication_score}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 col-span-2 sm:col-span-1">
                  <span className="text-[10px] text-slate-400 block">Relevance</span>
                  <span className="font-bold text-white text-sm">{turnFeedback.relevance_score}</span>
                </div>
              </div>

              <div className="text-xs text-slate-300 bg-slate-900/80 p-3.5 rounded-xl border border-slate-800 space-y-1.5">
                <div><span className="text-indigo-400 font-semibold">Feedback: </span>{turnFeedback.feedback}</div>
                <div><span className="text-emerald-400 font-semibold">Strengths: </span>{turnFeedback.key_strengths}</div>
                <div><span className="text-amber-400 font-semibold">Improvement: </span>{turnFeedback.improvement_areas}</div>
              </div>

              <div className="flex justify-end pt-2">
                <button
                  onClick={handleNextQuestion}
                  className="flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md transition"
                >
                  {currentQIndex < activeInterview.questions.length - 1 ? 'Proceed to Next Question' : 'Complete Simulation'}
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Completed Report Card */}
      {completedReport && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-emerald-500/40 shadow-2xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <h3 className="text-base font-bold text-white">Interview Simulation Report Finalized</h3>
            </div>
            <span className="text-sm font-extrabold text-emerald-400">
              Session Score: {completedReport.overall_score}/100
            </span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">{completedReport.summary}</p>
        </div>
      )}

      {/* Historical Sessions */}
      <div className="p-6 rounded-2xl glass-card space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
            <History className="w-4 h-4" /> Past Mock Interview Sessions
          </h3>
          <span className="text-xs text-slate-400">{history.length} Completed</span>
        </div>

        {history.length === 0 ? (
          <p className="text-xs text-slate-400 py-4 text-center">No past interviews recorded yet.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {history.map((h) => (
              <div key={h.id} className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white">{h.interview_type} Round</span>
                    <span className="text-[10px] font-mono px-2 py-0.2 rounded bg-slate-800 text-slate-300">
                      {h.status}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">{h.target_role}</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">{h.created_at}</div>
                </div>

                <div className="text-right">
                  <span className="text-base font-extrabold text-indigo-400">{h.overall_score}</span>
                  <span className="text-[10px] text-slate-400 block">/ 100</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
