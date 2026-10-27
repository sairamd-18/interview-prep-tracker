import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import ProfileModal from './components/ProfileModal';

// Pages
import LandingPage from './pages/LandingPage';
import DashboardPage from './pages/DashboardPage';
import SkillAssessmentPage from './pages/SkillAssessmentPage';
import StudyPlannerPage from './pages/StudyPlannerPage';
import CodingPracticePage from './pages/CodingPracticePage';
import MockInterviewPage from './pages/MockInterviewPage';
import ResumeAnalyzerPage from './pages/ResumeAnalyzerPage';
import ProgressAnalyticsPage from './pages/ProgressAnalyticsPage';

function AppContent() {
  const { user } = useAuth();
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [showProfileModal, setShowProfileModal] = useState(false);

  // Render full-width landing page if on 'landing' or if no user is authenticated
  if (currentPage === 'landing' || !user) {
    return (
      <LandingPage onGetStarted={() => setCurrentPage('dashboard')} />
    );
  }

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 antialiased font-['Plus_Jakarta_Sans',sans-serif]">
      {/* Sidebar Navigation */}
      <Sidebar
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-x-hidden">
        <Navbar
          currentPage={currentPage}
          onOpenProfile={() => setShowProfileModal(true)}
        />

        <main className="flex-1 pb-12">
          {currentPage === 'dashboard' && <DashboardPage onNavigate={(p) => setCurrentPage(p)} />}
          {currentPage === 'assessment' && <SkillAssessmentPage />}
          {currentPage === 'planner' && <StudyPlannerPage />}
          {currentPage === 'coding' && <CodingPracticePage />}
          {currentPage === 'interview' && <MockInterviewPage />}
          
          
          {currentPage === 'analytics' && <ProgressAnalyticsPage />}
        </main>
      </div>

      {/* Profile Settings Modal */}
      <ProfileModal
        isOpen={showProfileModal}
        onClose={() => setShowProfileModal(false)}
      />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
