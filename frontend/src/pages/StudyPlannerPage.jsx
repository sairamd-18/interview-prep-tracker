import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  CalendarDays, 
  CheckCircle2, 
  Clock, 
  Sparkles, 
  Plus, 
  AlertCircle, 
  RefreshCw,
  Tag,
  Check,
  Calendar,
  Filter,
  CheckCheck,
  X
} from 'lucide-react';

export default function StudyPlannerPage() {
  const [planData, setPlanData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterPriority, setFilterPriority] = useState('ALL');
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [adaptationMessage, setAdaptationMessage] = useState(null);
  
  // New task modal
  const [showModal, setShowModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newPriority, setNewPriority] = useState('High');
  const [newMinutes, setNewMinutes] = useState(60);

  const loadPlan = async () => {
    try {
      const data = await api.getCurrentPlan();
      setPlanData(data);
    } catch (err) {
      console.error('Failed to load plan:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlan();
  }, []);

  const handleToggle = async (taskId) => {
    try {
      await api.toggleTask(taskId);
      loadPlan();
    } catch (err) {
      console.error(err);
    }
  };

  // Agent 2: Regenerate Plan with AI
  const handleRegenerate = async () => {
    setIsRegenerating(true);
    setAdaptationMessage(null);
    try {
      const result = await api.generatePlan(true);
      await loadPlan();
      
      const msg = result.adaptation_note || 
        `AI Plan successfully recalibrated! ${result.tasks_updated_or_added || 8} customized tasks generated for ${result.target_role || 'your target role'}.`;
      setAdaptationMessage(msg);
    } catch (err) {
      console.error('Regenerate plan failed:', err);
      setAdaptationMessage('Failed to regenerate plan. Please try again.');
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleAddTask = async (e) => {
    e.preventDefault();
    try {
      await api.addTask({
        title: newTitle,
        description: newDesc,
        priority: newPriority,
        estimated_minutes: parseInt(newMinutes, 10)
      });
      setShowModal(false);
      setNewTitle('');
      setNewDesc('');
      loadPlan();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading personalized adaptive study plan...</div>;
  }

  const tasks = planData?.tasks || [];
  const filteredTasks = tasks.filter(t => {
    if (filterPriority === 'ALL') return true;
    return t.priority === filterPriority;
  });

  const adherence = planData?.adherence_rate || 0;
  const plan = planData?.plan;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="p-6 rounded-2xl glass-card flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <CalendarDays className="w-4 h-4" /> Agent 2: Study Planning Engine
          </div>
          <h2 className="text-xl font-bold text-white">{plan?.title || 'Adaptive Placement Study Plan'}</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Auto-prioritizes your diagnostic weak areas with higher frequency drills while balancing revision schedules.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition"
          >
            <Plus className="w-3.5 h-3.5" /> Add Custom Task
          </button>
          
          {/* Main AI Button: Regenerate Plan with AI */}
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition transform active:scale-95 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRegenerating ? 'animate-spin' : ''}`} />
            {isRegenerating ? 'Adapting Plan with AI...' : 'Regenerate Plan with AI'}
          </button>
        </div>
      </div>

      {/* Success Notification Banner on AI Adaptation */}
      {adaptationMessage && (
        <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-950/60 to-slate-900 border border-emerald-500/40 text-xs flex items-center justify-between text-emerald-300 animate-fadeIn shadow-lg">
          <div className="flex items-center gap-2.5">
            <Sparkles className="w-4 h-4 text-emerald-400 shrink-0 animate-bounce" />
            <span>{adaptationMessage}</span>
          </div>
          <button
            onClick={() => setAdaptationMessage(null)}
            className="text-slate-400 hover:text-white p-1"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Progress & Filters Banner */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium">Plan Adherence</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-extrabold text-white">{adherence}%</span>
            <span className="text-xs text-indigo-400">
              {planData?.completed_tasks} of {planData?.total_tasks} completed
            </span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
            <div className="bg-indigo-500 h-full rounded-full transition-all duration-500" style={{ width: `${adherence}%` }} />
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium">Target Interview Date</span>
          <div className="text-sm font-bold text-white mt-1">
            {plan?.target_date || 'In 4 Weeks'}
          </div>
          <span className="text-[11px] text-slate-400 mt-2 block">
            {plan?.total_weeks || 4} Weeks Preparation Runway
          </span>
        </div>

        <div className="md:col-span-2 p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-[11px] text-slate-400 font-medium">Filter by Priority</span>
            <div className="flex items-center gap-2 mt-2">
              {['ALL', 'High', 'Medium', 'Low'].map((p) => (
                <button
                  key={p}
                  onClick={() => setFilterPriority(p)}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                    filterPriority === p
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                      : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          <div className="text-right text-xs text-slate-400">
            Showing <span className="text-white font-bold">{filteredTasks.length}</span> tasks
          </div>
        </div>
      </div>

      {/* Task List */}
      <div className="space-y-3">
        {filteredTasks.length === 0 ? (
          <div className="p-12 text-center text-slate-400 glass-card rounded-2xl">
            No tasks found matching this priority filter.
          </div>
        ) : (
          filteredTasks.map((task) => (
            <div
              key={task.id}
              className={`p-4 rounded-xl border transition flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                task.is_completed
                  ? 'bg-slate-900/30 border-slate-800/40 opacity-60'
                  : 'bg-slate-900/80 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-start gap-3.5">
                <button
                  onClick={() => handleToggle(task.id)}
                  className={`mt-0.5 w-5 h-5 rounded-lg border flex items-center justify-center transition shrink-0 ${
                    task.is_completed
                      ? 'bg-emerald-600 border-emerald-500 text-white'
                      : 'border-slate-600 hover:border-indigo-400 bg-slate-950'
                  }`}
                >
                  {task.is_completed && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                </button>

                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <h4 className={`text-xs sm:text-sm font-semibold ${
                      task.is_completed ? 'line-through text-slate-400' : 'text-slate-100'
                    }`}>
                      {task.title}
                    </h4>

                    {task.topic_name && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                        {task.topic_name}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 mt-1">{task.description}</p>
                </div>
              </div>

              <div className="flex items-center gap-3 shrink-0 self-end sm:self-center">
                <div className="flex items-center gap-1 text-[11px] text-slate-400">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{task.estimated_minutes} min</span>
                </div>

                <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
                  task.priority === 'High'
                    ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                    : task.priority === 'Medium'
                    ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                    : 'bg-slate-800 text-slate-400 border-slate-700'
                }`}>
                  {task.priority} Priority
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Add Custom Task Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white">Add Custom Study Task</h3>
            <form onSubmit={handleAddTask} className="space-y-3">
              <div>
                <label className="block text-xs text-slate-400 mb-1">Task Title</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Read Operating Systems Paging Chapter"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-400 mb-1">Description</label>
                <textarea
                  rows={2}
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Specific focus areas, chapters, or problem sets..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Priority</label>
                  <select
                    value={newPriority}
                    onChange={(e) => setNewPriority(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Minutes</label>
                  <input
                    type="number"
                    value={newMinutes}
                    onChange={(e) => setNewMinutes(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition"
                >
                  Save Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
