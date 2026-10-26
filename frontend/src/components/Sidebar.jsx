import React from 'react';
import { 
  LayoutDashboard, 
  BrainCircuit, 
  CalendarDays, 
  Code2, 
  MessageSquareCode, 
  FileText, 
  BarChart3, 
  Bot,
  Sparkles
} from 'lucide-react';

export default function Sidebar({ currentPage, setCurrentPage }) {
  // Only the 7 essential preparation modules for clean presentation and demo
  const navItems = [
    { id: 'dashboard', label: 'Student Dashboard', icon: LayoutDashboard },
    { id: 'assessment', label: 'Skill Assessment', icon: BrainCircuit, badge: 'Agent 1' },
    { id: 'planner', label: 'Adaptive Planner', icon: CalendarDays, badge: 'Agent 2' },
    { id: 'coding', label: 'Coding Practice', icon: Code2, badge: 'Agent 3' },
    { id: 'interview', label: 'Mock Interview', icon: MessageSquareCode, badge: 'Agent 4' },
    { id: 'resume', label: 'Resume Analyzer', icon: FileText, badge: 'Agent 5' },
    { id: 'analytics', label: 'Progress & Research', icon: BarChart3, badge: 'Agent 6' },
  ];

  return (
    <aside className="w-64 bg-slate-900/90 border-r border-slate-800 flex flex-col h-screen sticky top-0 shrink-0 select-none">
      {/* Brand */}
      <div className="p-5 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setCurrentPage('dashboard')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <Sparkles className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <h1 className="font-bold text-base bg-gradient-to-r from-white via-slate-100 to-indigo-200 bg-clip-text text-transparent">
              PrepAgent AI
            </h1>
            <p className="text-[11px] text-slate-400 font-medium">Placement Multi-Agent</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          Preparation Modules
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all group ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 transition-colors ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-indigo-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className={`text-[10px] px-1.5 py-0.5 rounded-md font-mono ${
                  isActive ? 'bg-indigo-700/80 text-indigo-100' : 'bg-slate-800 text-slate-400 group-hover:bg-slate-700 group-hover:text-slate-300'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Orchestrator Status Card */}
      <div className="p-3 border-t border-slate-800/80">
        <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs">
          <div className="flex items-center justify-between mb-1.5">
            <div className="flex items-center gap-1.5">
              <Bot className="w-3.5 h-3.5 text-emerald-400" />
              <span className="font-semibold text-slate-200">AI Orchestrator</span>
            </div>
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
          </div>
          <p className="text-[11px] text-slate-400">
            6 Specialized Agents synced with event cascade feedback.
          </p>
        </div>
      </div>
    </aside>
  );
}
