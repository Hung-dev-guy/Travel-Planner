import React from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import ChatbotPage from '../pages/ChatbotPage';
import SearchPage from '../pages/SearchPage';
import TripPlannerPage from '../pages/trip/TripPlannerPage';
import TripPlanResultPage from '../pages/trip/TripPlanResultPage';
import TripDayDetailPage from '../pages/trip/TripDayDetailPage';
import DashboardPage from '../pages/DashboardPage';
import SettingsPage from '../pages/SettingsPage';
import FeaturesPage from '../pages/FeaturesPage';
import AboutPage from '../pages/AboutPage';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';

const ProtectedRoute = ({ children }) => {
  const user = localStorage.getItem('user');
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      
      <Route path="/planner" element={<ProtectedRoute><TripPlannerPage /></ProtectedRoute>} />
      <Route path="/trip-plan" element={<ProtectedRoute><TripPlanResultPage /></ProtectedRoute>} />
      <Route path="/trip-plan/day/:dayId" element={<ProtectedRoute><TripDayDetailPage /></ProtectedRoute>} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/chat" element={<ProtectedRoute><ChatbotPage /></ProtectedRoute>} />
      <Route path="/destinations" element={<ProtectedRoute><SearchPage /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
      
      <Route path="/features" element={<FeaturesPage />} />
      <Route path="/about" element={<AboutPage />} />
    </Routes>
  );
};

export default AppRoutes;
