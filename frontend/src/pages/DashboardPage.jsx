import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import ReadinessGauge from '../components/ReadinessGauge';
import { 
  AlertTriangle, 
  CheckCircle2, 
  Code2, 
  ArrowRight, 
  Sparkles, 
  Calendar, 
  TrendingUp, 
  Award,
  BookOpen,
  Bot,
  RefreshCw,
  X
} from 'lucide-react';

export default function DashboardPage({ onNavigate }) {
  const [dashboardData, setDashboardData] = useState(null);
  const [studyPlan, setStudyPlan] = useState(null);
  const [codingRecs, setCodingRecs] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [syncNotice, setSyncNotice] = useState(null);

  const loadAll = async () => {
    try {
      const [dash, plan, recs, activity] = await Promise.all([
        api.getDashboard(),
        api.getCurrentPlan(),
        api.getCodingRecommendations(3),
        api.getRecentActivity()
      ]);
      setDashboardData(dash);
      setStudyPlan(plan);
      setCodingRecs(recs.recommended_problems || []);
      setRecentActivity(activity || []);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  const handleToggleTask = async (taskId) => {
    try {
      await api.toggleTask(taskId);
      // Refresh plan and dashboard score
      const [newPlan, newDash] = await Promise.all([
        api.getCurrentPlan(),
        api.getDashboard()
      ]);
      setStudyPlan(newPlan);
      setDashboardData(newDash);
    } catch (err) {
      console.error(err);
    }
  };

  const handleManualRefresh = async () => {
    setRefreshing(true);
    setSyncNotice(null);
    await loadAll();
    setSyncNotice('✨ All 6 Autonomous Agents Synced: Readiness Score and Task Priorities Recalibrated!');
    setTimeout(() => {
      setSyncNotice(null);
    }, 4500);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3 text-slate-400">
        <RefreshCw className="w-6 h-6 animate-spin text-indigo-500" />
        <span className="text-sm">Orchestrating agent insights & readiness metrics...</span>
      </div>
    );
  }

  const readinessScore = dashboardData?.overall_readiness_score || 0;
  const weakTopics = dashboardData?.weak_topics || [];
  const tasks = studyPlan?.tasks?.slice(0, 4) || [];
  const nextActions = dashboardData?.recommended_next_actions || [];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Banner: Quick Summary & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-indigo-900/30 via-slate-900/40 to-purple-900/30 p-5 rounded-2xl border border-indigo-500/20 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              Adaptive Placement Engine Active
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Live Feedback Loop
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Readiness calibrated continuously across your quizzes, code submissions, and mock answers.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Sync Agents Button */}
          <button
            onClick={handleManualRefresh}
            disabled={refreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 border border-slate-700 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin text-indigo-400' : ''}`} />
            Sync Agents
          </button>
          <button
            onClick={() => onNavigate('assessment')}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white shadow-md shadow-indigo-600/25 transition"
          >
            Take Quick Diagnostic <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Sync Success Notification */}
      {syncNotice && (
        <div className="p-3.5 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-xs text-emerald-300 flex items-center justify-between shadow-lg animate-fadeIn">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{syncNotice}</span>
          </div>
          <button onClick={() => setSyncNotice(null)} className="text-slate-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Grid: Gauge + Weak Areas + Next Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Placement Readiness Gauge Card */}
        <div className="lg:col-span-4 p-6 rounded-2xl glass-card flex flex-col items-center justify-between text-center relative overflow-hidden">
          <div className="w-full flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="font-semibold text-slate-300">Composite Readiness</span>
            <span className="text-[10px] font-mono bg-slate-800 px-2 py-0.5 rounded">Agent 6</span>
          </div>

          <ReadinessGauge score={readinessScore} size={190} />

          <div className="grid grid-cols-2 gap-2 w-full mt-4 text-left text-xs">
            <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-slate-400 text-[11px] block">Coding Solved</span>
              <span className="font-bold text-white text-sm">
                {dashboardData?.coding_progress?.solved_count} / {dashboardData?.coding_progress?.total_problems}
              </span>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-slate-400 text-[11px] block">Resume ATS</span>
              <span className="font-bold text-white text-sm">
                {dashboardData?.resume_score}%
              </span>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-slate-400 text-[11px] block">Mock Rating</span>
              <span className="font-bold text-white text-sm">
                {dashboardData?.mock_interview_performance?.average_score}/100
              </span>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-slate-400 text-[11px] block">Plan Adherence</span>
              <span className="font-bold text-white text-sm">
                {dashboardData?.study_plan_adherence}%
              </span>
            </div>
          </div>
        </div>

        {/* Weak Topics Diagnostic Alert */}
        <div className="lg:col-span-8 space-y-6">
          <div className="p-6 rounded-2xl glass-card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <h3 className="text-sm font-bold text-white">Detected Competency Weak Areas</h3>
              </div>
              <button 
                onClick={() => onNavigate('assessment')}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
              >
                View Full Skill Matrix <ArrowRight className="w-3 h-3" />
              </button>
            </div>

            {weakTopics.length === 0 ? (
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs">
                No weak topics currently flagged! All evaluated domains are above 50% proficiency.
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {weakTopics.map((wt, i) => (
                  <div key={i} className="p-3.5 rounded-xl bg-slate-900/80 border border-rose-500/20 flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs font-bold text-slate-100">{wt.topic_name}</span>
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-300 font-mono">
                          Weak
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-400">{wt.subject_name}</span>
                    </div>

                    <div className="text-right">
                      <span className="text-sm font-extrabold text-rose-400">{wt.proficiency_score}%</span>
                      <button
                        onClick={() => onNavigate('coding')}
                        className="block text-[10px] text-indigo-400 hover:underline mt-0.5"
                      >
                        Target Practice →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* AI Next Actions Bar */}
            {nextActions.length > 0 && (
              <div className="mt-4 pt-4 border-t border-slate-800">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                  Agent Orchestrator Recommendations
                </span>
                <div className="space-y-2">
                  {nextActions.slice(0, 2).map((act, i) => (
                    <div key={i} className="p-2.5 rounded-xl bg-indigo-950/40 border border-indigo-800/40 flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <Sparkles className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                        <div>
                          <span className="font-semibold text-slate-200">{act.title}: </span>
                          <span className="text-slate-400 text-[11px]">{act.reason}</span>
                        </div>
                      </div>
                      <button
                        onClick={() => {
                          if (act.action_type === 'mock_interview') onNavigate('interview');
                          else if (act.action_type === 'resume') onNavigate('resume');
                          else if (act.action_type === 'study_plan') onNavigate('planner');
                          else onNavigate('coding');
                        }}
                        className="text-xs font-medium text-indigo-300 hover:text-white px-2 py-1 rounded bg-indigo-900/60 hover:bg-indigo-800 transition shrink-0 ml-2"
                      >
                        Execute
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Lower Row: Study Tasks & Coding Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Adaptive Study Tasks */}
        <div className="p-6 rounded-2xl glass-card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-indigo-400" />
              <h3 className="text-sm font-bold text-white">Upcoming Adaptive Study Tasks</h3>
            </div>
            <button 
              onClick={() => onNavigate('planner')}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
            >
              Open Planner <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-2.5">
            {tasks.length === 0 ? (
              <p className="text-xs text-slate-400 py-4 text-center">No pending study tasks.</p>
            ) : (
              tasks.map((task) => (
                <div
                  key={task.id}
                  className={`p-3 rounded-xl border transition flex items-start justify-between gap-3 ${
                    task.is_completed ? 'bg-slate-900/40 border-slate-800/60 opacity-60' : 'bg-slate-900/80 border-slate-800'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <button
                      onClick={() => handleToggleTask(task.id)}
                      className={`mt-0.5 w-4 h-4 rounded border flex items-center justify-center transition ${
                        task.is_completed ? 'bg-emerald-600 border-emerald-500 text-white' : 'border-slate-600 hover:border-indigo-400'
                      }`}
                    >
                      {task.is_completed && <CheckCircle2 className="w-3.5 h-3.5" />}
                    </button>
                    <div>
                      <div className={`text-xs font-semibold ${task.is_completed ? 'line-through text-slate-400' : 'text-slate-200'}`}>
                        {task.title}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">{task.description}</div>
                    </div>
                  </div>

                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full shrink-0 ${
                    task.priority === 'High' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 'bg-slate-800 text-slate-300'
                  }`}>
                    {task.priority}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recommended Coding Problems */}
        <div className="p-6 rounded-2xl glass-card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Code2 className="w-4 h-4 text-purple-400" />
              <h3 className="text-sm font-bold text-white">Curated Problem Recommendations</h3>
            </div>
            <button 
              onClick={() => onNavigate('coding')}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
            >
              Practice All <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-2.5">
            {codingRecs.length === 0 ? (
              <p className="text-xs text-slate-400 py-4 text-center">No pending coding recommendations.</p>
            ) : (
              codingRecs.map((prob) => (
                <div
                  key={prob.id}
                  onClick={() => onNavigate('coding')}
                  className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-purple-500/40 cursor-pointer transition group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-200 group-hover:text-purple-300 transition">
                      {prob.title}
                    </span>
                    <span className={`text-[10px] px-2 py-0.5 rounded font-mono ${
                      prob.difficulty === 'Easy' ? 'bg-emerald-500/10 text-emerald-400' :
                      prob.difficulty === 'Medium' ? 'bg-amber-500/10 text-amber-400' : 'bg-rose-500/10 text-rose-400'
                    }`}>
                      {prob.difficulty}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1 line-clamp-1">
                    <span className="text-indigo-400 font-medium">Why: </span>{prob.recommendation_reason}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
