import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Components
import Navbar from './components/layout/Navbar';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Pages
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Calendars from './pages/Calendars';
import SchedulingLinks from './pages/SchedulingLinks';
import SchedulingLink from './pages/SchedulingLink';
import CreateLinkPage from './pages/CreateLinkPage';
import SettingsPage from './pages/SettingsPage';
import NotFound from './pages/NotFound';
import PublicSchedulingPage from './pages/PublicSchedulingPage';

// Create a client
const queryClient = new QueryClient();

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return children;
};

function AppRoutes() {
  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/book/:slug" element={<PublicSchedulingPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <div>
                <Navbar />
                <div className="container mx-auto px-4 py-8">
                  <Dashboard />
                </div>
              </div>
            </ProtectedRoute>
          }
        />
        <Route
          path="/calendars"
          element={
            <ProtectedRoute>
              <div>
                <Navbar />
                <div className="container mx-auto px-4 py-8">
                  <Calendars />
                </div>
              </div>
            </ProtectedRoute>
          }
        />
        <Route
          path="/scheduling-links"
          element={
            <ProtectedRoute>
              <div>
                <Navbar />
                <div className="container mx-auto px-4 py-8">
                  <SchedulingLinks />
                </div>
              </div>
            </ProtectedRoute>
          }
        />
        <Route path="/scheduling-links/create" element={<ProtectedRoute><CreateLinkPage /></ProtectedRoute>} />
        <Route path="/scheduling-links/create" element={<SchedulingLink />} />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <div>
                <Navbar />
                <div className="container mx-auto px-4 py-8">
                  <SettingsPage />
                </div>
              </div>
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </Router>
    </QueryClientProvider>
  );
}

export default App; 