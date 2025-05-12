import React from 'react';
import GoogleCalendarConnect from '../components/settings/GoogleCalendarConnect';
import SchedulingWindows from '../components/settings/SchedulingWindows';

function SettingsPage() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-2xl font-semibold text-gray-900 mb-6">Settings</h1>
          <div className="space-y-6">
            <GoogleCalendarConnect />
            <SchedulingWindows />
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage; 