import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  BrainCircuit, 
  CheckCircle2, 
  XCircle, 
  HelpCircle, 
  Clock, 
  Award, 
  ArrowRight, 
  RotateCcw,
  Sparkles,
  Layers,
  ChevronRight,
  TrendingUp
} from 'lucide-react';

export default function SkillAssessmentPage() {
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  
  // Quiz State
  const [quizQuestions, setQuizQuestions] = useState([]);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [quizResult, setQuizResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quizActive, setQuizActive] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Skill matrix overview
  const [skillProfile, setSkillProfile] = useState(null);

  useEffect(() => {
    loadSubjectsAndProfile();
  }, []);

  const loadSubjectsAndProfile = async () => {
    try {
      const [subjs, prof] = await Promise.all([
        api.getSubjects(),
        api.getSkillProfile()
      ]);
      setSubjects(subjs);
      setSkillProfile(prof);
      if (subjs.length > 0 && !selectedSubject) {
        handleSelectSubject(subjs[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSubject = async (subj) => {
    setSelectedSubject(subj);
    setSelectedTopic(null);
    try {
      const topList = await api.getTopicsBySubject(subj.id);
      setTopics(topList);
    } catch (err) {
      console.error(err);
    }
  };

  const startQuiz = async (topicId = null) => {
    setLoading(true);
    try {
      const questions = await api.getQuiz({
        subject_id: selectedSubject?.id,
        topic_id: topicId || undefined,
        limit: 4
      });
      setQuizQuestions(questions);
      setSelectedAnswers({});
      setCurrentQIndex(0);
      setQuizResult(null);
      setQuizActive(true);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOptionSelect = (optIndex) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [currentQIndex]: optIndex
    });
  };

  const handleSubmitQuiz = async () => {
    setSubmitting(true);
    try {
      const answersPayload = quizQuestions.map((q, idx) => ({
        question_id: q.id,
        selected_option: selectedAnswers[idx] !== undefined ? selectedAnswers[idx] : 0
      }));

      const res = await api.submitQuiz({
        subject_id: selectedSubject.id,
        topic_id: selectedTopic?.id || null,
        answers: answersPayload,
        time_taken_seconds: 45
      });

      setQuizResult(res);
      // Refresh skill profiles to display updated scores
      const updatedProf = await api.getSkillProfile();
      setSkillProfile(updatedProf);
      // Also refresh topics of current subject
      const topList = await api.getTopicsBySubject(selectedSubject.id);
      setTopics(topList);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading && subjects.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] text-slate-400">
        Loading assessment matrices...
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="p-6 rounded-2xl glass-card flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <BrainCircuit className="w-4 h-4" /> Agent 1: Skill Assessment Engine
          </div>
          <h2 className="text-xl font-bold text-white">Continuous Competency Profiler</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Test topic-level aptitude across 7 core computer science and behavioral domains. Quiz evaluations trigger Bayesian updates on your evolving skill profile.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => startQuiz(null)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition"
          >
            <Sparkles className="w-4 h-4" /> Start {selectedSubject?.code || 'Subject'} Diagnostic
          </button>
        </div>
      </div>

      {/* Active Quiz View */}
      {quizActive && quizQuestions.length > 0 && !quizResult && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-indigo-500/30 shadow-2xl relative">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800 text-xs text-slate-400 mb-6">
            <div className="flex items-center gap-2">
              <span className="font-bold text-white">{selectedSubject?.name}</span>
              <span>•</span>
              <span className="text-indigo-400">
                Question {currentQIndex + 1} of {quizQuestions.length}
              </span>
            </div>
            <button
              onClick={() => setQuizActive(false)}
              className="text-slate-400 hover:text-white"
            >
              Cancel Quiz
            </button>
          </div>

          {/* Current Question */}
          {(() => {
            const q = quizQuestions[currentQIndex];
            const currentSelected = selectedAnswers[currentQIndex];

            return (
              <div className="space-y-6 max-w-3xl mx-auto">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
                    Topic: {q.topic_name}
                  </span>
                  <span className="text-xs font-medium text-slate-400">
                    Difficulty: <span className="text-amber-400">{q.difficulty}</span>
                  </span>
                </div>

                <h3 className="text-base sm:text-lg font-semibold text-slate-100 leading-relaxed">
                  {q.question_text}
                </h3>

                {/* Options */}
                <div className="space-y-3">
                  {q.options.map((opt, optIdx) => {
                    const isSelected = currentSelected === optIdx;
                    return (
                      <button
                        key={optIdx}
                        onClick={() => handleOptionSelect(optIdx)}
                        className={`w-full text-left p-3.5 rounded-xl text-xs sm:text-sm font-medium transition flex items-center justify-between border ${
                          isSelected
                            ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-md shadow-indigo-600/10'
                            : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:bg-slate-800/80 hover:border-slate-700'
                        }`}
                      >
                        <span>{opt}</span>
                        <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                          isSelected ? 'border-indigo-400 bg-indigo-500' : 'border-slate-600'
                        }`}>
                          {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                        </div>
                      </button>
                    );
                  })}
                </div>

                {/* Navigation Buttons */}
                <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                  <button
                    disabled={currentQIndex === 0}
                    onClick={() => setCurrentQIndex(currentQIndex - 1)}
                    className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium disabled:opacity-40"
                  >
                    Previous
                  </button>

                  {currentQIndex < quizQuestions.length - 1 ? (
                    <button
                      onClick={() => setCurrentQIndex(currentQIndex + 1)}
                      className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-1.5"
                    >
                      Next Question <ChevronRight className="w-4 h-4" />
                    </button>
                  ) : (
                    <button
                      onClick={handleSubmitQuiz}
                      disabled={submitting}
                      className="px-6 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-600/30 flex items-center gap-1.5"
                    >
                      {submitting ? 'Evaluating with Agent 1...' : 'Submit Assessment'}
                    </button>
                  )}
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* Quiz Results View */}
      {quizResult && (
        <div className="p-6 rounded-2xl bg-slate-900 border border-emerald-500/30 shadow-2xl space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
            <div>
              <span className="text-xs text-emerald-400 font-bold uppercase tracking-wider">Assessment Complete</span>
              <h3 className="text-lg font-bold text-white mt-0.5">
                Diagnostic Score: {quizResult.score_percentage}% ({quizResult.correct_answers}/{quizResult.total_questions} Correct)
              </h3>
            </div>
            <button
              onClick={() => { setQuizResult(null); setQuizActive(false); }}
              className="px-4 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300"
            >
              Done & Return to Subjects
            </button>
          </div>

          {/* Detailed Question Review */}
          <div className="space-y-4">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Answer Review & Explanations</h4>
            {quizResult.detailed_results.map((res, i) => (
              <div key={i} className={`p-4 rounded-xl border ${
                res.is_correct ? 'bg-emerald-950/20 border-emerald-500/30' : 'bg-rose-950/20 border-rose-500/30'
              }`}>
                <div className="flex items-center gap-2 mb-2">
                  {res.is_correct ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <XCircle className="w-4 h-4 text-rose-400" />
                  )}
                  <span className="text-xs font-semibold text-slate-200">
                    Question {i+1}: {res.question_text}
                  </span>
                </div>
                <div className="text-xs text-slate-300 mt-2 space-y-1">
                  <div>Your Answer: <span className={res.is_correct ? 'text-emerald-400 font-medium' : 'text-rose-400 font-medium'}>
                    {res.options[res.selected_option]}
                  </span></div>
                  {!res.is_correct && (
                    <div>Correct Answer: <span className="text-emerald-400 font-medium">
                      {res.options[res.correct_answer]}
                    </span></div>
                  )}
                  <div className="text-slate-400 mt-2 text-[11px] bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
                    <span className="text-indigo-300 font-semibold">Explanation: </span>{res.explanation}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Layout: Subjects Tabs + Topics & Skill Profiles */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Subjects List */}
        <div className="lg:col-span-4 space-y-3">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider px-1">
            Subject Domains
          </h3>
          <div className="space-y-2">
            {subjects.map((subj) => {
              const isSelected = selectedSubject?.id === subj.id;
              return (
                <div
                  key={subj.id}
                  onClick={() => handleSelectSubject(subj)}
                  className={`p-4 rounded-xl border cursor-pointer transition flex items-center justify-between ${
                    isSelected
                      ? 'bg-indigo-600/15 border-indigo-500 shadow-md shadow-indigo-600/10'
                      : 'bg-slate-900/70 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs ${
                      isSelected ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-300'
                    }`}>
                      {subj.code}
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-200">{subj.name}</h4>
                      <span className="text-[11px] text-slate-400">{subj.topic_count} Topics</span>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className={`text-xs font-extrabold ${
                      subj.user_proficiency >= 75 ? 'text-emerald-400' :
                      subj.user_proficiency >= 50 ? 'text-indigo-400' : 'text-rose-400'
                    }`}>
                      {subj.user_proficiency}%
                    </span>
                    <span className="text-[10px] text-slate-400 block">Proficiency</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Topics in Selected Subject with Skill Profile Badges */}
        <div className="lg:col-span-8 space-y-4">
          <div className="flex items-center justify-between px-1">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              {selectedSubject?.name} • Topic Competency Matrix
            </h3>
            <span className="text-xs text-slate-400">
              {topics.length} Evaluated Topics
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {topics.map((top) => {
              const status = top.status;
              const badgeClass = status === 'Strong'
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : status === 'Weak'
                ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20';

              return (
                <div
                  key={top.id}
                  className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between gap-3 hover:border-slate-700 transition"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="text-xs font-bold text-white">{top.name}</h4>
                      <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">{top.description}</p>
                    </div>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border shrink-0 ${badgeClass}`}>
                      {status}
                    </span>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-xs">
                    <div>
                      <span className="text-slate-400 text-[11px]">Score: </span>
                      <span className="font-bold text-white">{top.proficiency_score}%</span>
                    </div>

                    <button
                      onClick={() => {
                        setSelectedTopic(top);
                        startQuiz(top.id);
                      }}
                      className="text-[11px] font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
                    >
                      Quiz Topic <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
