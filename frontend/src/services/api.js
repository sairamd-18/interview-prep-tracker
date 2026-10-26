/**
 * Central API Client for interacting with FastAPI Backend.
 */

const API_BASE = '/api';

function getAuthHeaders() {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
}

function buildQueryString(params = {}) {
  const clean = {};
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '' && v !== 'undefined' && v !== 'null') {
      clean[k] = v;
    }
  }
  const qs = new URLSearchParams(clean).toString();
  return qs ? `?${qs}` : '';
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = options.isFormData ? (
    localStorage.getItem('token') ? { 'Authorization': `Bearer ${localStorage.getItem('token')}` } : {}
  ) : {
    ...getAuthHeaders(),
    ...options.headers
  };

  const config = {
    ...options,
    headers
  };

  if (options.body && !options.isFormData && typeof options.body === 'object') {
    config.body = JSON.stringify(options.body);
  }

  const response = await fetch(url, config);
  if (!response.ok) {
    let errorDetail = 'API request failed';
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || errorDetail;
    } catch {
      errorDetail = await response.text() || errorDetail;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  // Auth
  login: (email, password) => request('/auth/login', { method: 'POST', body: { email, password } }),
  register: (data) => request('/auth/register', { method: 'POST', body: data }),
  getMe: () => request('/auth/me'),

  // Profile
  getProfile: () => request('/profile'),
  updateProfile: (data) => request('/profile/update', { method: 'PUT', body: data }),

  // Skill Assessment
  getSubjects: () => request('/assessment/subjects'),
  getTopicsBySubject: (subjectId) => request(`/assessment/topics/${subjectId}`),
  getQuiz: (params = {}) => request(`/assessment/quiz${buildQueryString(params)}`),
  submitQuiz: (data) => request('/assessment/submit', { method: 'POST', body: data }),
  getSkillProfile: () => request('/assessment/skill-profile'),

  // Study Planner
  getCurrentPlan: () => request('/planner/current'),
  generatePlan: (forceRegenerate = true) => request('/planner/generate', { method: 'POST', body: { force_regenerate: forceRegenerate } }),
  toggleTask: (taskId) => request(`/planner/tasks/${taskId}/toggle`, { method: 'POST' }),
  addTask: (data) => request('/planner/tasks', { method: 'POST', body: data }),

  // Coding Practice
  getProblems: (params = {}) => request(`/coding/problems${buildQueryString(params)}`),
  getProblemBySlug: (slug) => request(`/coding/problems/${slug}`),
  submitCode: (problemId, code, language = 'python') => request('/coding/submit', { method: 'POST', body: { problem_id: problemId, code, language } }),
  getCodingRecommendations: (limit = 4) => request(`/coding/recommendations${buildQueryString({ limit })}`),
  getCodingHistory: () => request('/coding/history'),

  // Mock Interview
  startInterview: (interviewType = 'Technical', targetRole) => request('/interview/start', { method: 'POST', body: { interview_type: interviewType, target_role: targetRole } }),
  submitInterviewAnswer: (interviewId, questionId, userResponse) => request('/interview/respond', { method: 'POST', body: { interview_id: interviewId, question_id: questionId, user_response: userResponse } }),
  completeInterview: (interviewId) => request('/interview/complete', { method: 'POST', body: { interview_id: interviewId } }),
  getInterviewHistory: () => request('/interview/history'),
  getInterviewDetails: (interviewId) => request(`/interview/${interviewId}`),

  // Resume Analyzer
  analyzeResumeText: (resumeText, targetRole, filename) => request('/resume/analyze', { method: 'POST', body: { resume_text: resumeText, target_role: targetRole, filename } }),
  uploadResumeFile: (formData) => request('/resume/upload', { method: 'POST', body: formData, isFormData: true }),
  getResumeHistory: () => request('/resume/history'),

  // Progress Analytics & System
  getDashboard: () => request('/analytics/dashboard'),
  getMetrics: () => request('/analytics/metrics'),
  getTrends: () => request('/analytics/trends'),
  getRecentActivity: () => request('/analytics/recent-activity'),
  getAgentsStatus: () => request('/system/agents'),
};
