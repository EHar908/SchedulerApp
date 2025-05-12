import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CreateLinkForm from '../components/scheduling/CreateLinkForm';

function CreateLinkPage() {
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (data) => {
    try {
      setIsSubmitting(true);
      setError(null);

      // Convert empty strings to null for optional fields and ensure correct types
      const cleanedData = {
        ...data,
        meeting_length: parseInt(data.meeting_length, 10),
        max_uses: data.maxUses ? parseInt(data.maxUses, 10) : null,
        max_days_ahead: parseInt(data.maxDaysAhead, 10),
        expiration_date: data.expirationDate ? `${data.expirationDate}T23:59:59` : null,
        custom_questions: data.custom_questions || []
      };

      // Remove the camelCase fields to avoid confusion
      delete cleanedData.maxUses;
      delete cleanedData.maxDaysAhead;
      delete cleanedData.expirationDate;

      console.log('Submitting data:', cleanedData);

      const response = await fetch('http://localhost:8000/api/scheduling-links', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(cleanedData)
      });

      console.log('Response status:', response.status);
      const responseText = await response.text();
      console.log('Response text:', responseText);

      if (!response.ok) {
        let errorMessage;
        try {
          const errorData = JSON.parse(responseText);
          if (Array.isArray(errorData.detail)) {
            // Handle validation errors
            errorMessage = errorData.detail.map(err => `${err.loc[1]}: ${err.msg}`).join(', ');
          } else {
            errorMessage = errorData.detail || 'Failed to create scheduling link';
          }
        } catch (e) {
          errorMessage = responseText || 'Failed to create scheduling link';
        }
        throw new Error(errorMessage);
      }

      const result = JSON.parse(responseText);
      console.log('Success response:', result);
      
      // Redirect to the scheduling links page
      navigate('/scheduling-links');
    } catch (error) {
      console.error('Error creating scheduling link:', error);
      setError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Create New Scheduling Link
          </h3>
          <div className="mt-2 max-w-xl text-sm text-gray-500">
            <p>
              Create a new scheduling link that others can use to book time with you.
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
            <CreateLinkForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default CreateLinkPage; 