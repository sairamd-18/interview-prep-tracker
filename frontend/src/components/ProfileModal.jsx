import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { X, Target, Calendar, Clock, Building, Award, Check } from 'lucide-react';

export default function ProfileModal({ isOpen, onClose }) {
  const { user, setUser } = useAuth();
  const [targetRole, setTargetRole] = useState('');
  const [targetCompany, setTargetCompany] = useState('');
  const [interviewDate, setInterviewDate] = useState('');
  const [dailyHours, setDailyHours] = useState(3.0);
  const [experienceLevel, setExperienceLevel] = useState('');
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (isOpen) {
      api.getProfile().then(data => {
        const p = data.profile || {};
        setTargetRole(p.target_role || 'Software Development Engineer (SDE)');
        setTargetCompany(p.target_company || 'Top Tech Product Companies');
        setInterviewDate(p.interview_date || '');
        setDailyHours(p.daily_study_hours || 3.0);
        setExperienceLevel(p.experience_level || 'Fresher / Entry Level');
      });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await api.updateProfile({
        target_role: targetRole,
        target_company: targetCompany,
        interview_date: interviewDate,
        daily_study_hours: parseFloat(dailyHours),
        experience_level: experienceLevel
      });
      // Update Auth context user target role
      if (user) {
        setUser({ ...user, target_role: targetRole });
      }
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        onClose();
      }, 700);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg"
        >
          <X className="w-5 h-5" />
        </button>

        <div>
          <h3 className="text-base font-bold text-white">Student Goals & Preparation Preferences</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Agents use these parameters to tailor study plans, interview questions, and problem difficulty.
          </p>
        </div>

        <form onSubmit={handleSave} className="space-y-3 pt-2">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5 text-indigo-400" /> Target Job Role
            </label>
            <input
              type="text"
              required
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              placeholder="e.g. Software Development Engineer (SDE)"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
              <Building className="w-3.5 h-3.5 text-purple-400" /> Target Companies / Tier
            </label>
            <input
              type="text"
              value={targetCompany}
              onChange={(e) => setTargetCompany(e.target.value)}
              placeholder="e.g. Google, Amazon, Microsoft, High-Growth Startups"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-blue-400" /> Target Interview Date
              </label>
              <input
                type="date"
                value={interviewDate}
                onChange={(e) => setInterviewDate(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-amber-400" /> Daily Study Hours
              </label>
              <input
                type="number"
                step="0.5"
                min="0.5"
                max="12"
                value={dailyHours}
                onChange={(e) => setDailyHours(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
              <Award className="w-3.5 h-3.5 text-emerald-400" /> Experience Level
            </label>
            <select
              value={experienceLevel}
              onChange={(e) => setExperienceLevel(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="Fresher / Entry Level">Fresher / Final Year Graduate (0-1 yrs)</option>
              <option value="Junior Engineer">Junior Engineer (1-2 yrs)</option>
              <option value="Mid-Level Engineer">Mid-Level Software Engineer (2-4 yrs)</option>
            </select>
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition flex items-center gap-1.5"
            >
              {success ? (
                <>
                  <Check className="w-3.5 h-3.5 text-white" /> Saved!
                </>
              ) : saving ? (
                'Saving...'
              ) : (
                'Save Preferences'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
