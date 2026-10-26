import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Target, Clock, User, LogOut, Sparkles } from 'lucide-react';

export default function Navbar({ currentPage, onOpenProfile }) {
  const { user, logout, loginAsDemo } = useAuth();

  const titleMap = {
    landing: 'Platform Overview & Agent Architecture',
    dashboard: 'Placement Readiness Dashboard',
    assessment: 'Skill Assessment Diagnostic Quizzes',
    planner: 'Adaptive Study Schedule & Milestone Planner',
    coding: 'Skill-Targeted Coding Practice & Runner',
    interview: 'Conversational AI Mock Interview Simulator',
    resume: 'ATS Resume Quality & Keyword Gap Analyzer',
    analytics: 'Multi-Agent Performance & Preparation Analytics',
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/60 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h2 className="text-base font-semibold text-white tracking-tight">
          {titleMap[currentPage] || 'Interview Preparation Tracker'}
        </h2>
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
          <span>Dynamic Adaptive System</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {user ? (
          <>
            <div className="hidden sm:flex items-center gap-2 bg-slate-800/80 border border-slate-700/60 px-3 py-1.5 rounded-xl text-xs">
              <Target className="w-3.5 h-3.5 text-indigo-400" />
              <span className="text-slate-300 font-medium">{user.target_role || 'SDE Candidate'}</span>
            </div>

            <div className="flex items-center gap-2.5 pl-2 border-l border-slate-800">
              <button 
                onClick={onOpenProfile}
                className="flex items-center gap-2 p-1.5 hover:bg-slate-800/60 rounded-xl transition text-left"
              >
                <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs shadow-inner">
                  {user.full_name ? user.full_name.charAt(0) : 'U'}
                </div>
                <div className="hidden md:block">
                  <div className="text-xs font-semibold text-slate-200 leading-none">{user.full_name}</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">{user.email}</div>
                </div>
              </button>

              <button
                onClick={logout}
                title="Sign Out"
                className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </>
        ) : (
          <button
            onClick={loginAsDemo}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-4 py-2 rounded-xl shadow-md shadow-indigo-600/25 transition"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Quick Demo Login
          </button>
        )}
      </div>
    </header>
  );
}
