import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  BarChart3, 
  TrendingUp, 
  Bot, 
  CheckCircle2, 
  Clock, 
  Layers, 
  Sparkles, 
  RefreshCw,
  Activity,
  Zap
} from 'lucide-react';

export default function ProgressAnalyticsPage() {
  const [metricsData, setMetricsData] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [met, dash, tr] = await Promise.all([
        api.getMetrics(),
        api.getDashboard(),
        api.getTrends()
      ]);
      setMetricsData(met);
      setDashboardData(dash);
      setTrends(tr || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading progress analytics & agent metrics...</div>;
  }

  const subjectProf = dashboardData?.subject_proficiency || {};
  const metrics = metricsData?.metrics || [];
  const agentStatuses = metricsData?.agents_status || [];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="p-6 rounded-2xl glass-card flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <BarChart3 className="w-4 h-4" /> Agent 6 & Orchestrator Metrics
          </div>
          <h2 className="text-xl font-bold text-white">System Diagnostics & Research Analytics</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Real-time monitoring of multi-agent execution times, assessment accuracy, study plan adherence, and overall readiness trajectories.
          </p>
        </div>

        <button
          onClick={loadData}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Refresh Metrics
        </button>
      </div>

      {/* 8 System Performance Metrics Grid */}
      <div className="space-y-3">
        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider px-1">
          The 8 Performance & Research Metrics
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {metrics.map((m, i) => (
            <div key={i} className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 hover:border-slate-700 transition">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400 font-medium">{m.name}</span>
                <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded ${
                  m.status === 'Optimal' || m.status === 'High' || m.status === 'Sub-50ms Fast'
                    ? 'bg-emerald-500/10 text-emerald-400'
                    : 'bg-indigo-500/10 text-indigo-400'
                }`}>
                  {m.status}
                </span>
              </div>
              <div className="text-2xl font-extrabold text-white">{m.value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Middle Row: Subject Proficiency Breakdown & Live Agent Status */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Subject-Wise Proficiency Bars (7 cols) */}
        <div className="lg:col-span-7 p-6 rounded-2xl glass-card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Subject Domain Proficiency Spectrum
            </h3>
            <span className="text-xs text-slate-400">Calculated across 7 disciplines</span>
          </div>

          <div className="space-y-3.5 pt-2">
            {[
              { label: 'Data Structures & Algorithms (DSA)', key: 'dsa' },
              { label: 'Database Management Systems (DBMS)', key: 'dbms' },
              { label: 'Operating Systems (OS)', key: 'os' },
              { label: 'Computer Networks (CN)', key: 'cn' },
              { label: 'Object-Oriented Programming (OOP)', key: 'oop' },
              { label: 'Quantitative & Logical Aptitude', key: 'apt' },
              { label: 'Behavioral & HR Competencies', key: 'beh' },
            ].map((s) => {
              const val = subjectProf[s.key] !== undefined ? subjectProf[s.key] : 50.0;
              const barColor = val >= 75 ? 'bg-emerald-500' : val >= 50 ? 'bg-indigo-500' : 'bg-rose-500';

              return (
                <div key={s.key} className="space-y-1 text-xs">
                  <div className="flex justify-between font-medium">
                    <span className="text-slate-300">{s.label}</span>
                    <span className="font-bold text-white">{val}%</span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${barColor}`}
                      style={{ width: `${val}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* 6 AI Agents Real-Time Monitor (5 cols) */}
        <div className="lg:col-span-5 p-6 rounded-2xl glass-card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Bot className="w-4 h-4 text-emerald-400" /> Live Agent Cluster Health
            </h3>
            <span className="text-[11px] font-mono text-emerald-400">All 6 Online</span>
          </div>

          <div className="space-y-2.5">
            {agentStatuses.map((ag, i) => (
              <div key={i} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/90 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2.5">
                  <span className="flex h-2 w-2 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                  <div>
                    <span className="font-semibold text-slate-200 block">{ag.agent}</span>
                    <span className="text-[10px] text-slate-400">{ag.calls} Execution Calls</span>
                  </div>
                </div>

                <div className="text-right font-mono text-[11px] text-slate-400">
                  <span className="text-white font-bold">{ag.avg_latency_ms}</span> ms
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Historical Readiness Trend Table */}
      <div className="p-6 rounded-2xl glass-card space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-indigo-400" /> Historical Readiness Trajectory Snapshots
          </h3>
          <span className="text-xs text-slate-400">{trends.length} Data Points Logged</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/90 text-slate-400 text-[11px] uppercase border-b border-slate-800">
              <tr>
                <th className="p-3">Timestamp</th>
                <th className="p-3">Readiness</th>
                <th className="p-3">DSA</th>
                <th className="p-3">DBMS</th>
                <th className="p-3">OS</th>
                <th className="p-3">Coding %</th>
                <th className="p-3">Resume</th>
                <th className="p-3">Adherence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {trends.slice(-8).reverse().map((tr, i) => (
                <tr key={i} className="hover:bg-slate-800/40">
                  <td className="p-3 text-slate-400 font-sans">{tr.recorded_at}</td>
                  <td className="p-3 font-bold text-indigo-300">{tr.readiness_score}%</td>
                  <td className="p-3">{tr.dsa_score}%</td>
                  <td className="p-3">{tr.dbms_score}%</td>
                  <td className="p-3">{tr.os_score}%</td>
                  <td className="p-3">{tr.coding_completion_pct}%</td>
                  <td className="p-3">{tr.resume_score}%</td>
                  <td className="p-3 text-emerald-400">{tr.study_plan_adherence}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
