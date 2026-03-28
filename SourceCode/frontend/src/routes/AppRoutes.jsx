import React from 'react';
import { Routes, Route } from 'react-router-dom';
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

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<TripPlannerPage />} />
      <Route path="/trip-plan" element={<TripPlanResultPage />} />
      <Route path="/trip-plan/day/:dayId" element={<TripDayDetailPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/chat" element={<ChatbotPage />} />
      <Route path="/search" element={<SearchPage />} />
      <Route path="/settings" element={<SettingsPage />} />
      <Route path="/features" element={<FeaturesPage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
    </Routes>
  );
};

export default AppRoutes;
