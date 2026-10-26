import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  Code2, 
  Play, 
  CheckCircle2, 
  AlertCircle, 
  ExternalLink, 
  Sparkles, 
  BookOpen, 
  ChevronRight, 
  Terminal,
  Clock,
  RotateCcw,
  RefreshCw,
  FileCheck
} from 'lucide-react';

const SOLUTION_TEMPLATES = {
  'two-sum': `def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []`,

  'climbing-stairs': `def climb_stairs(n: int) -> int:
    if n <= 2:
        return n
    prev2, prev1 = 1, 2
    for _ in range(3, n + 1):
        prev2, prev1 = prev1, prev2 + prev1
    return prev1`,

  'longest-substring-without-repeating-characters': `def length_of_longest_substring(s: str) -> int:
    char_index = {}
    max_len = 0
    start = 0
    for end, char in enumerate(s):
        if char in char_index and char_index[char] >= start:
            start = char_index[char] + 1
        char_index[char] = end
        max_len = max(max_len, end - start + 1)
    return max_len`,

  'coin-change': `def coin_change(coins: list[int], amount: int) -> int:
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for i in range(coin, amount + 1):
            dp[i] = min(dp[i], dp[i - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1`,

  'zero-one-knapsack': `def knapsack(weights: list[int], values: list[int], W: int) -> int:
    n = len(weights)
    dp = [0] * (W + 1)
    for i in range(n):
        for w in range(W, weights[i] - 1, -1):
            dp[w] = max(dp[w], values[i] + dp[w - weights[i]])
    return dp[W]`,

  'reverse-linked-list': `def reverse_list(head):
    prev = None
    curr = head
    while curr:
        next_temp = curr.next
        curr.next = prev
        prev = curr
        curr = next_temp
    return prev`,

  'maximum-depth-of-binary-tree': `def max_depth(root) -> int:
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))`,

  'number-of-islands': `def num_islands(grid: list[list[str]]) -> int:
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    islands = 0
    def dfs(r, c):
        if r < 0 or c < 0 or r >= rows or c >= cols or grid[r][c] != '1':
            return
        grid[r][c] = '0'
        dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1)
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                islands += 1
                dfs(r, c)
    return islands`
};

export default function CodingPracticePage() {
  const [problems, setProblems] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [resources, setResources] = useState([]);
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [code, setCode] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterDiff, setFilterDiff] = useState('ALL');
  const [refreshingRecs, setRefreshingRecs] = useState(false);

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    try {
      const [probs, recData] = await Promise.all([
        api.getProblems(),
        api.getCodingRecommendations(4)
      ]);
      setProblems(probs);
      setRecommendations(recData.recommended_problems || []);
      setResources(recData.learning_resources || []);

      if (recData.recommended_problems && recData.recommended_problems.length > 0) {
        handleSelectProblem(recData.recommended_problems[0]);
      } else if (probs.length > 0) {
        handleSelectProblem(probs[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshRecs = async () => {
    setRefreshingRecs(true);
    try {
      const recData = await api.getCodingRecommendations(4);
      setRecommendations(recData.recommended_problems || []);
    } catch (err) {
      console.error(err);
    } finally {
      setRefreshingRecs(false);
    }
  };

  const handleSelectProblem = async (prob) => {
    setSubmissionResult(null);
    try {
      const fullProblem = await api.getProblemBySlug(prob.slug);
      setSelectedProblem(fullProblem);
      setCode(fullProblem.last_submission?.code || fullProblem.starter_code || '# Write your Python code here\n');
    } catch (err) {
      setSelectedProblem(prob);
      setCode(prob.starter_code || '# Write code here\n');
    }
  };

  const handleLoadDemoSolution = () => {
    if (!selectedProblem) return;
    const sol = SOLUTION_TEMPLATES[selectedProblem.slug];
    if (sol) {
      setCode(sol);
    } else {
      setCode(selectedProblem.starter_code ? selectedProblem.starter_code.replace('pass', 'return True') : 'def solve(): return True');
    }
  };

  const handleSubmitCode = async () => {
    if (!selectedProblem) return;
    setSubmitting(true);
    try {
      const res = await api.submitCode(selectedProblem.id, code, 'python');
      setSubmissionResult(res);
      // Refresh list to update solved state
      const updatedProbs = await api.getProblems();
      setProblems(updatedProbs);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading coding challenges & AI recommendations...</div>;
  }

  const filteredProblems = problems.filter(p => {
    if (filterDiff === 'ALL') return true;
    return p.difficulty === filterDiff;
  });

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="p-6 rounded-2xl glass-card flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Code2 className="w-4 h-4" /> Agent 3: Coding Recommendation Engine
          </div>
          <h2 className="text-xl font-bold text-white">Targeted Technical Problem Solving</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Recommends coding drills calibrated to your skill gaps. Difficulty scales progressively, prioritizing weak areas and filtering completed challenges.
          </p>
        </div>

        <button
          onClick={handleRefreshRecs}
          disabled={refreshingRecs}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshingRecs ? 'animate-spin' : ''}`} />
          Refresh Recommendations
        </button>
      </div>

      {/* AI Recommendation Banner */}
      {recommendations.length > 0 && (
        <div className="p-4 rounded-2xl bg-gradient-to-r from-purple-950/40 via-indigo-950/40 to-slate-900 border border-purple-500/20">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-xs font-bold text-purple-300">
              <Sparkles className="w-4 h-4 text-purple-400" />
              Agent 3 Priority Problem Set (Tailored to Weak Competencies)
            </div>
            <span className="text-[11px] text-slate-400 font-mono">Dynamic Difficulty Scaling</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {recommendations.map((rec) => (
              <div
                key={rec.id}
                onClick={() => handleSelectProblem(rec)}
                className={`p-3.5 rounded-xl border cursor-pointer transition ${
                  selectedProblem?.id === rec.id
                    ? 'bg-purple-600/20 border-purple-500 shadow-md shadow-purple-600/10'
                    : 'bg-slate-900/80 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-100">{rec.title}</span>
                  <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${
                    rec.difficulty === 'Easy' ? 'bg-emerald-500/10 text-emerald-400' :
                    rec.difficulty === 'Medium' ? 'bg-amber-500/10 text-amber-400' : 'bg-rose-500/10 text-rose-400'
                  }`}>
                    {rec.difficulty}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 mt-2 line-clamp-2">
                  <span className="text-purple-400 font-medium">Why: </span>{rec.recommendation_reason}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Workspace: Left Problem Browser + Right Interactive Editor */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Problem List (4 cols) */}
        <div className="lg:col-span-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">All Problems</span>
            <div className="flex gap-1 text-[11px]">
              {['ALL', 'Easy', 'Medium', 'Hard'].map((d) => (
                <button
                  key={d}
                  onClick={() => setFilterDiff(d)}
                  className={`px-2 py-0.5 rounded transition ${
                    filterDiff === d ? 'bg-indigo-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2 max-h-[680px] overflow-y-auto pr-1">
            {filteredProblems.map((p) => {
              const isSelected = selectedProblem?.id === p.id;
              return (
                <div
                  key={p.id}
                  onClick={() => handleSelectProblem(p)}
                  className={`p-3 rounded-xl border cursor-pointer transition flex items-center justify-between ${
                    isSelected
                      ? 'bg-indigo-600/15 border-indigo-500 shadow-sm'
                      : 'bg-slate-900/70 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    {p.is_solved ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border border-slate-700 shrink-0" />
                    )}
                    <div>
                      <div className="text-xs font-bold text-slate-200">{p.title}</div>
                      <div className="text-[10px] text-slate-400">{p.topic_name}</div>
                    </div>
                  </div>

                  <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                    p.difficulty === 'Easy' ? 'text-emerald-400 bg-emerald-500/10' :
                    p.difficulty === 'Medium' ? 'text-amber-400 bg-amber-500/10' : 'text-rose-400 bg-rose-500/10'
                  }`}>
                    {p.difficulty}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Curated Resources */}
          {resources.length > 0 && (
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2 mt-4">
              <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                Recommended Study Guides
              </span>
              {resources.map((res, i) => (
                <a
                  key={i}
                  href={res.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-2 rounded-lg bg-slate-950/60 border border-slate-800/80 hover:border-indigo-500/40 text-xs transition"
                >
                  <div className="font-semibold text-slate-200 flex items-center justify-between">
                    <span>{res.title}</span>
                    <ExternalLink className="w-3 h-3 text-slate-400" />
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">{res.description}</div>
                </a>
              ))}
            </div>
          )}
        </div>

        {/* Code Editor & Problem Workspace (8 cols) */}
        <div className="lg:col-span-8 space-y-4">
          {selectedProblem ? (
            <div className="p-6 rounded-2xl glass-card space-y-4">
              {/* Problem Title & Details */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-white">{selectedProblem.title}</h3>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                      selectedProblem.difficulty === 'Easy' ? 'bg-emerald-500/10 text-emerald-400' :
                      selectedProblem.difficulty === 'Medium' ? 'bg-amber-500/10 text-amber-400' : 'bg-rose-500/10 text-rose-400'
                    }`}>
                      {selectedProblem.difficulty}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    {selectedProblem.subject_name} • {selectedProblem.topic_name}
                  </div>
                </div>

                <div className="text-xs text-slate-400">
                  Acceptance: <span className="text-white font-semibold">{selectedProblem.acceptance_rate}%</span>
                </div>
              </div>

              {/* Description */}
              <div className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3.5 rounded-xl border border-slate-800/80 whitespace-pre-wrap">
                {selectedProblem.description}
              </div>

              {/* Code Editor Header & Demo Helper */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span className="font-mono flex items-center gap-1.5 text-indigo-400">
                    <Terminal className="w-3.5 h-3.5" /> Python 3 Solution
                  </span>
                  
                  <div className="flex items-center gap-2">
                    {/* Demo Accelerator Button */}
                    <button
                      type="button"
                      onClick={handleLoadDemoSolution}
                      className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-indigo-950/80 hover:bg-indigo-900 border border-indigo-500/30 text-indigo-300 text-[11px] font-medium transition"
                      title="Load optimal working solution for demo presentation"
                    >
                      <Sparkles className="w-3 h-3 text-indigo-400" />
                      Load Optimal Solution (Demo)
                    </button>

                    <button
                      onClick={() => setCode(selectedProblem.starter_code || '')}
                      className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-slate-200"
                    >
                      <RotateCcw className="w-3 h-3" /> Reset
                    </button>
                  </div>
                </div>

                <div className="relative rounded-xl overflow-hidden border border-slate-800 focus-within:border-indigo-500 transition">
                  <textarea
                    rows={12}
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    className="w-full bg-slate-950 p-4 font-mono text-xs text-indigo-100 focus:outline-none resize-y leading-relaxed"
                    spellCheck="false"
                  />
                </div>
              </div>

              {/* Action Bar */}
              <div className="flex items-center justify-between pt-2">
                <div className="text-xs text-slate-400">
                  Submissions trigger real-time multi-agent orchestrator recalculation.
                </div>

                <button
                  onClick={handleSubmitCode}
                  disabled={submitting}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-600/25 transition disabled:opacity-50"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  {submitting ? 'Testing Code...' : 'Run & Submit Code'}
                </button>
              </div>

              {/* Submission Result Output */}
              {submissionResult && (
                <div className={`p-4 rounded-xl border mt-4 text-xs ${
                  submissionResult.status === 'Accepted'
                    ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-200'
                    : 'bg-rose-950/30 border-rose-500/40 text-rose-200'
                }`}>
                  <div className="flex items-center justify-between font-bold text-sm mb-1">
                    <span className="flex items-center gap-1.5">
                      {submissionResult.status === 'Accepted' ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-rose-400" />
                      )}
                      {submissionResult.status}
                    </span>
                    <span className="text-xs font-mono font-normal">
                      Runtime: {submissionResult.execution_time_ms} ms
                    </span>
                  </div>
                  <p className="text-xs opacity-90 mt-1">{submissionResult.feedback}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="p-12 text-center text-slate-400 glass-card rounded-2xl">
              Select a problem from the left or recommendations above to begin practicing.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
