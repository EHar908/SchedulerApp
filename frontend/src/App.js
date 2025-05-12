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

// Create a client
const queryClient = new QueryClient();

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" />;
};

function AppRoutes() {
  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/calendars" element={<ProtectedRoute><Calendars /></ProtectedRoute>} />
        <Route path="/scheduling-links" element={<ProtectedRoute><SchedulingLinks /></ProtectedRoute>} />
        <Route path="/scheduling-links/create" element={<ProtectedRoute><CreateLinkPage /></ProtectedRoute>} />
        <Route path="/s/:slug" element={<SchedulingLink />} />
        <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
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