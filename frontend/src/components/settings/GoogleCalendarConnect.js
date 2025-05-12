import React, { useState, useEffect } from 'react';

function GoogleCalendarConnect() {
  const [calendars, setCalendars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCalendars();
  }, []);

  const fetchCalendars = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('http://localhost:8000/auth/google/calendars', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch calendars');
      }
      const data = await response.json();
      setCalendars(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    try {
      const response = await fetch('http://localhost:8000/auth/google/auth', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to start Google auth');
      }
      const data = await response.json();
      window.location.href = data.authorization_url;
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDisconnect = async (calendarId) => {
    try {
      const response = await fetch(`http://localhost:8000/auth/google/calendars/${calendarId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to disconnect calendar');
      }

      setCalendars(prev => prev.filter(cal => cal.id !== calendarId));
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="bg-white shadow sm:rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">
          Connected Google Calendars
        </h3>
        <div className="mt-2 max-w-xl text-sm text-gray-500">
          <p>
            Connect your Google Calendar accounts to show your availability.
          </p>
        </div>
        {error && (
          <div className="mt-4 bg-red-50 border-l-4 border-red-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}
        <div className="mt-5">
          {loading ? (
            <div className="text-gray-500">Loading...</div>
          ) : (
            <div className="space-y-4">
              {calendars.map(calendar => (
                <div key={calendar.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">{calendar.email}</p>
                      <p className="text-xs text-gray-500">Connected {new Date(calendar.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleDisconnect(calendar.id)}
                    className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    Disconnect
                  </button>
                </div>
              ))}
              <button
                type="button"
                onClick={handleConnect}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Connect Google Calendar
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default GoogleCalendarConnect; 