import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  BrainCircuit, 
  CalendarDays, 
  Code2, 
  MessageSquareCode, 
  FileText, 
  BarChart3, 
  ArrowRight, 
  CheckCircle2, 
  Sparkles,
  Bot,
  Zap,
  TrendingUp,
  ShieldCheck
} from 'lucide-react';

export default function LandingPage({ onGetStarted }) {
  const { user, loginAsDemo, login, register } = useAuth();
  const [authMode, setAuthMode] = useState('demo'); // 'demo' | 'login' | 'register'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [targetRole, setTargetRole] = useState('Software Development Engineer (SDE)');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAuth = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (authMode === 'login') {
        await login(email, password);
      } else if (authMode === 'register') {
        await register({ email, password, full_name: fullName, target_role: targetRole });
      }
      onGetStarted();
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoClick = async () => {
    setLoading(true);
    try {
      await loginAsDemo();
      onGetStarted();
    } catch (err) {
      setError('Failed to login demo account: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const agents = [
    {
      num: 1,
      title: 'Skill Assessment Agent',
      icon: BrainCircuit,
      color: 'from-blue-500 to-indigo-600',
      description: 'Continuously analyzes diagnostic quizzes across 7 core disciplines (DSA, DBMS, OS, CN, OOP, Aptitude, Behavioral) and pinpoints exact topic weaknesses.'
    },
    {
      num: 2,
      title: 'Study Planning Agent',
      icon: CalendarDays,
      color: 'from-indigo-500 to-purple-600',
      description: 'Generates an adaptive daily & weekly preparation roadmap prioritizing weak areas and calibrating automatically when performance shifts.'
    },
    {
      num: 3,
      title: 'Coding Recommendation Agent',
      icon: Code2,
      color: 'from-purple-500 to-pink-600',
      description: 'Recommends targeted programming challenges matching skill readiness with explainable tags, scaling difficulty and filtering out solved problems.'
    },
    {
      num: 4,
      title: 'Mock Interview Agent',
      icon: MessageSquareCode,
      color: 'from-pink-500 to-rose-600',
      description: 'Conducts interactive conversational technical and behavioral simulations, evaluating answers across 5 metrics with actionable feedback.'
    },
    {
      num: 5,
      title: 'Resume Analysis Agent',
      icon: FileText,
      color: 'from-amber-500 to-orange-600',
      description: 'Parses resumes against specific target job benchmarks, calculating ATS compatibility, detecting missing keywords, and formulating improvements.'
    },
    {
      num: 6,
      title: 'Progress Monitoring Agent',
      icon: BarChart3,
      color: 'from-emerald-500 to-teal-600',
      description: 'Central brain computing the dynamic composite Placement Readiness Score (0-100%), historical trend trajectories, and next-best actions.'
    }
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Hero Section */}
      <div className="relative overflow-hidden pt-12 pb-20 px-6 sm:px-12 border-b border-slate-800">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute top-20 -right-40 w-96 h-96 bg-purple-600/15 rounded-full blur-3xl pointer-events-none"></div>

        <div className="max-w-6xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-6 shadow-sm">
            <Sparkles className="w-3.5 h-3.5" />
            Autonomous Multi-Agent AI Interview Architecture
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight sm:leading-none mb-6">
            Agentic AI <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">Placement Tracker</span>
          </h1>

          <p className="text-slate-400 text-base sm:text-xl max-w-3xl mx-auto mb-10 leading-relaxed font-normal">
            Move beyond static checklist trackers. A 6-agent cognitive architecture that continuously assesses your technical competencies, adapts your study plan, recommends coding drills, simulates interviews, and predicts your true placement readiness.
          </p>

          {/* Quick Access Card */}
          <div className="max-w-md mx-auto p-6 rounded-2xl glass-card border border-slate-800 shadow-2xl text-left">
            {user ? (
              <div className="text-center space-y-4">
                <div className="w-12 h-12 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center mx-auto text-emerald-400">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Welcome back, {user.full_name}!</h3>
                  <p className="text-xs text-slate-400">You are logged in as {user.email}</p>
                </div>
                <button
                  onClick={onGetStarted}
                  className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition"
                >
                  Enter Preparation Dashboard <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div>
                <div className="flex border-b border-slate-800 mb-4 pb-2 text-xs font-semibold text-slate-400 gap-4">
                  <button 
                    onClick={() => setAuthMode('demo')} 
                    className={`pb-1 ${authMode === 'demo' ? 'text-indigo-400 border-b-2 border-indigo-500' : 'hover:text-slate-200'}`}
                  >
                    Quick Demo
                  </button>
                  <button 
                    onClick={() => setAuthMode('login')} 
                    className={`pb-1 ${authMode === 'login' ? 'text-indigo-400 border-b-2 border-indigo-500' : 'hover:text-slate-200'}`}
                  >
                    Login
                  </button>
                  <button 
                    onClick={() => setAuthMode('register')} 
                    className={`pb-1 ${authMode === 'register' ? 'text-indigo-400 border-b-2 border-indigo-500' : 'hover:text-slate-200'}`}
                  >
                    Register
                  </button>
                </div>

                {error && (
                  <div className="mb-4 p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
                    {error}
                  </div>
                )}

                {authMode === 'demo' ? (
                  <div className="space-y-4">
                    <p className="text-xs text-slate-400 leading-relaxed">
                      Experience the platform immediately with our pre-loaded candidate profile (<span className="text-indigo-300 font-mono">Alex Mercer</span>), loaded with active quizzes, study schedule, and real-time weak topic calibrations.
                    </p>
                    <button
                      onClick={handleDemoClick}
                      disabled={loading}
                      className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition"
                    >
                      <Sparkles className="w-4 h-4" />
                      {loading ? 'Launching Session...' : 'Explore Demo Dashboard (Instant)'}
                    </button>
                  </div>
                ) : (
                  <form onSubmit={handleAuth} className="space-y-3">
                    {authMode === 'register' && (
                      <div>
                        <label className="block text-[11px] font-medium text-slate-400 mb-1">Full Name</label>
                        <input
                          type="text"
                          required
                          value={fullName}
                          onChange={(e) => setFullName(e.target.value)}
                          placeholder="e.g. Maya Lin"
                          className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                        />
                      </div>
                    )}
                    <div>
                      <label className="block text-[11px] font-medium text-slate-400 mb-1">Email Address</label>
                      <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="you@university.edu"
                        className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-400 mb-1">Password</label>
                      <input
                        type="password"
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="••••••••"
                        className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full py-2.5 mt-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition"
                    >
                      {loading ? 'Processing...' : (authMode === 'login' ? 'Sign In' : 'Create Student Account')}
                    </button>
                  </form>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 6 Specialized Agents Showcase */}
      <div className="max-w-6xl mx-auto py-16 px-6 sm:px-12">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3">
            Six Specialized Autonomous Agents
          </h2>
          <p className="text-slate-400 text-sm max-w-2xl mx-auto">
            Each agent operates on a designated domain responsibility, exchanging feedback signals through the central orchestration loop.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((ag) => {
            const Icon = ag.icon;
            return (
              <div key={ag.num} className="p-6 rounded-2xl glass-card glass-card-hover border border-slate-800 relative">
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-10 h-10 rounded-xl bg-gradient-to-tr ${ag.color} flex items-center justify-center text-white shadow-md`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-full bg-slate-800 text-indigo-400 border border-slate-700">
                    Agent 0{ag.num}
                  </span>
                </div>
                <h3 className="text-base font-bold text-white mb-2">{ag.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{ag.description}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Adaptive Workflow Loop Diagram */}
      <div className="bg-slate-900/60 border-y border-slate-800 py-16 px-6 sm:px-12">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-white mb-2">The Closed-Loop Adaptive Workflow</h2>
            <p className="text-xs text-slate-400">See how one agent's diagnostic finding triggers an automated cascade across the platform.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
            <div className="p-5 rounded-xl bg-slate-950/70 border border-slate-800">
              <div className="w-8 h-8 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center mx-auto mb-3 font-bold text-xs">
                1
              </div>
              <h4 className="text-sm font-semibold text-white mb-1">Diagnostic Signal</h4>
              <p className="text-xs text-slate-400">
                Student scores 35% on Dynamic Programming quiz. Skill Assessment Agent updates skill profile to <span className="text-rose-400 font-semibold">Weak</span>.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-slate-950/70 border border-slate-800">
              <div className="w-8 h-8 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto mb-3 font-bold text-xs">
                2
              </div>
              <h4 className="text-sm font-semibold text-white mb-1">Cascaded Adaptation</h4>
              <p className="text-xs text-slate-400">
                Study Planner schedules DP theory drill. Coding Recommender surfaces Easy DP problems (Climbing Stairs) with explainability.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-slate-950/70 border border-slate-800">
              <div className="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto mb-3 font-bold text-xs">
                3
              </div>
              <h4 className="text-sm font-semibold text-white mb-1">Readiness Recalibration</h4>
              <p className="text-xs text-slate-400">
                Progress Monitoring Agent dynamically computes placement readiness, tracks adherence, and adjusts next best actions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
