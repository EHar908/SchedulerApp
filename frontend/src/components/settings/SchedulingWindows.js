import React, { useState, useEffect } from 'react';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const HOURS = Array.from({ length: 24 }, (_, i) => i);

function SchedulingWindows() {
  const [windows, setWindows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedHours, setSelectedHours] = useState({});

  useEffect(() => {
    fetchWindows();
  }, []);

  const fetchWindows = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('http://localhost:8000/api/scheduling-windows', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch scheduling windows');
      }
      const data = await response.json();
      setWindows(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddWindow = async (day) => {
    try {
      const { startHour, endHour } = selectedHours[day] || {};
      if (startHour === undefined || endHour === undefined) {
        setError('Please select both start and end hours');
        return;
      }

      // Format hours as HH:MM strings
      const formattedStartHour = `${startHour.toString().padStart(2, '0')}:00`;
      const formattedEndHour = `${endHour.toString().padStart(2, '0')}:00`;

      console.log('Adding window:', { 
        day_of_week: day, 
        start_hour: formattedStartHour, 
        end_hour: formattedEndHour 
      });

      const response = await fetch('http://localhost:8000/api/scheduling-windows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          day_of_week: day,
          start_hour: formattedStartHour,
          end_hour: formattedEndHour,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to add scheduling window');
      }

      const newWindow = await response.json();
      setWindows(prev => [...prev, newWindow]);
      
      // Clear selected hours for this day
      setSelectedHours(prev => ({
        ...prev,
        [day]: undefined
      }));
    } catch (err) {
      console.error('Error adding window:', err);
      setError(err.message);
    }
  };

  const handleDeleteWindow = async (windowId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/scheduling-windows/${windowId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete scheduling window');
      }

      setWindows(prev => prev.filter(window => window.id !== windowId));
    } catch (err) {
      console.error('Error deleting window:', err);
      setError(err.message);
    }
  };

  const handleHourChange = (day, type, value) => {
    setSelectedHours(prev => ({
      ...prev,
      [day]: {
        ...prev[day],
        [type]: parseInt(value)
      }
    }));
  };

  return (
    <div className="bg-white shadow sm:rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">
          Scheduling Windows
        </h3>
        <div className="mt-2 max-w-xl text-sm text-gray-500">
          <p>
            Define your available hours for each day of the week.
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
        
        {loading ? (
          <div className="text-gray-500">Loading...</div>
        ) : (
          <div className="space-y-4">
            {DAYS.map((day, dayIndex) => (
              <div key={day} className="border rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">{day}</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Start Hour</label>
                    <select
                      className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                      value={selectedHours[dayIndex]?.startHour || ''}
                      onChange={(e) => handleHourChange(dayIndex, 'startHour', e.target.value)}
                    >
                      <option value="">Select start hour</option>
                      {HOURS.map((hour) => (
                        <option key={hour} value={hour}>
                          {hour}:00
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">End Hour</label>
                    <select
                      className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                      value={selectedHours[dayIndex]?.endHour || ''}
                      onChange={(e) => handleHourChange(dayIndex, 'endHour', e.target.value)}
                    >
                      <option value="">Select end hour</option>
                      {HOURS.map((hour) => (
                        <option key={hour} value={hour}>
                          {hour}:00
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="mt-4">
                  <button
                    type="button"
                    onClick={() => handleAddWindow(dayIndex)}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Add Window
                  </button>
                </div>
                {windows
                  .filter((window) => window.day_of_week === dayIndex)
                  .map((window) => (
                    <div key={window.id} className="flex items-center justify-between bg-gray-50 p-2 rounded mt-2">
                      <span className="text-sm text-gray-600">
                        {window.start_hour} - {window.end_hour}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleDeleteWindow(window.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        Delete
                      </button>
                    </div>
                  ))}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default SchedulingWindows; 