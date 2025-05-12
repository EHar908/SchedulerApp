import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { format, parseISO } from 'date-fns';

function PublicSchedulingPage() {
  const { slug } = useParams();
  const [schedulingLink, setSchedulingLink] = useState(null);
  const [availableSlots, setAvailableSlots] = useState({});
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedTime, setSelectedTime] = useState(null);
  const [step, setStep] = useState('select-time'); // select-time, enter-details
  const [formData, setFormData] = useState({
    email: '',
    linkedin_url: '',
    answers: {}
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSchedulingLink = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/scheduling-links/slug/${slug}`);
        if (!response.ok) {
          throw new Error('Scheduling link not found');
        }
        const data = await response.json();
        setSchedulingLink(data);
      } catch (error) {
        setError(error.message);
      }
    };

    fetchSchedulingLink();
  }, [slug]);

  useEffect(() => {
    const fetchAvailableSlots = async () => {
      if (!schedulingLink) return;
      try {
        const response = await fetch(`http://localhost:8000/api/scheduling-links/${schedulingLink.id}/available-slots`);
        if (!response.ok) {
          throw new Error('Failed to fetch available slots');
        }
        const data = await response.json();
        setAvailableSlots(data);
      } catch (error) {
        setError(error.message);
      }
    };

    fetchAvailableSlots();
  }, [schedulingLink]);

  const handleDateSelect = (date) => {
    setSelectedDate(date);
    setSelectedTime(null);
  };

  const handleTimeSelect = (time) => {
    setSelectedTime(time);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAnswerChange = (questionId, value) => {
    setFormData(prev => ({
      ...prev,
      answers: {
        ...prev.answers,
        [questionId]: value
      }
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedDate || !selectedTime) return;

    // Create a date object in the local timezone
    const [hours, minutes] = selectedTime.split(':').map(Number);
    const meetingTime = new Date(selectedDate);
    meetingTime.setHours(hours, minutes, 0, 0);
    
    // Convert to UTC while preserving the local time
    // Instead of using getTimezoneOffset, we'll use the ISO string directly
    // This ensures the day of week is preserved
    const utcMeetingTime = new Date(meetingTime.toISOString());
    
    try {
      const response = await fetch(`http://localhost:8000/api/scheduling-links/${schedulingLink.id}/book`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          meeting_time: utcMeetingTime.toISOString()
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to book meeting');
      }

      // Show success message or redirect
      setStep('success');
    } catch (error) {
      setError(error.message);
    }
  };

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-red-600">Error</h2>
            <p className="mt-2 text-gray-600">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!schedulingLink) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (step === 'success') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-green-600">Success!</h2>
            <p className="mt-2 text-gray-600">Your meeting has been scheduled successfully.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-lg shadow p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">{schedulingLink.title}</h1>

          {step === 'select-time' ? (
            <div>
              <h2 className="text-xl font-semibold mb-4">Select a Date and Time</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Date Selection */}
                <div>
                  <h3 className="text-lg font-medium mb-2">Available Dates</h3>
                  <div className="space-y-2">
                    {Object.keys(availableSlots).map(date => (
                      <button
                        key={date}
                        onClick={() => handleDateSelect(date)}
                        className={`w-full p-3 text-left rounded ${
                          selectedDate === date
                            ? 'bg-indigo-100 border-indigo-500'
                            : 'bg-white border-gray-300'
                        } border hover:bg-gray-50`}
                      >
                        {format(parseISO(date), 'EEEE, MMMM d, yyyy')}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Time Selection */}
                {selectedDate && (
                  <div>
                    <h3 className="text-lg font-medium mb-2">Available Times</h3>
                    <div className="grid grid-cols-2 gap-2">
                      {availableSlots[selectedDate].map(time => (
                        <button
                          key={time}
                          onClick={() => handleTimeSelect(time)}
                          className={`p-3 text-center rounded ${
                            selectedTime === time
                              ? 'bg-indigo-100 border-indigo-500'
                              : 'bg-white border-gray-300'
                          } border hover:bg-gray-50`}
                        >
                          {time}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {selectedTime && (
                <div className="mt-8">
                  <button
                    onClick={() => setStep('enter-details')}
                    className="w-full bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700"
                  >
                    Continue
                  </button>
                </div>
              )}
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  id="email"
                  required
                  value={formData.email}
                  onChange={handleInputChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label htmlFor="linkedin_url" className="block text-sm font-medium text-gray-700">
                  LinkedIn URL
                </label>
                <input
                  type="url"
                  name="linkedin_url"
                  id="linkedin_url"
                  required
                  value={formData.linkedin_url}
                  onChange={handleInputChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>

              {schedulingLink.custom_questions.map(question => (
                <div key={question.id}>
                  <label htmlFor={`question-${question.id}`} className="block text-sm font-medium text-gray-700">
                    {question.question}
                    {question.required && <span className="text-red-500">*</span>}
                  </label>
                  <textarea
                    id={`question-${question.id}`}
                    required={question.required}
                    value={formData.answers[question.id] || ''}
                    onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    rows={3}
                  />
                </div>
              ))}

              <div className="flex justify-between">
                <button
                  type="button"
                  onClick={() => setStep('select-time')}
                  className="bg-white text-gray-700 py-2 px-4 border border-gray-300 rounded hover:bg-gray-50"
                >
                  Back
                </button>
                <button
                  type="submit"
                  className="bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700"
                >
                  Schedule Meeting
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export default PublicSchedulingPage; 