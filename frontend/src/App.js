import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Components
import Navbar from './components/layout/Navbar';

// Pages
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Calendars from './pages/Calendars';
import SchedulingLinks from './pages/SchedulingLinks';
import SchedulingLink from './pages/SchedulingLink';
import CreateLinkPage from './pages/CreateLinkPage';
import NotFound from './pages/NotFound';

// Create a client
const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-100">
          <Navbar />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/login" element={<Login />} />
            <Route path="/calendars" element={<Calendars />} />
            <Route path="/scheduling-links" element={<SchedulingLinks />} />
            <Route path="/scheduling-links/create" element={<CreateLinkPage />} />
            <Route path="/s/:slug" element={<SchedulingLink />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App; 