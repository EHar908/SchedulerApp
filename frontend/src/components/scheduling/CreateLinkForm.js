import React, { useState } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { XMarkIcon } from '@heroicons/react/24/outline';

function CreateLinkForm({ onSubmit, isSubmitting }) {
  const { register, handleSubmit, formState: { errors }, control } = useForm({
    defaultValues: {
      custom_questions: []
    }
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "custom_questions"
  });

  const addQuestion = () => {
    append({ question: '', required: false, type: 'text' });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">
          Meeting Title
        </label>
        <input
          type="text"
          id="title"
          {...register('title', { required: 'Title is required' })}
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          disabled={isSubmitting}
        />
        {errors.title && (
          <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="meeting_length" className="block text-sm font-medium text-gray-700">
          Meeting Duration (minutes)
        </label>
        <input
          type="number"
          id="meeting_length"
          {...register('meeting_length', { 
            required: 'Duration is required',
            min: { value: 15, message: 'Minimum duration is 15 minutes' },
            max: { value: 480, message: 'Maximum duration is 8 hours' }
          })}
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          disabled={isSubmitting}
        />
        {errors.meeting_length && (
          <p className="mt-1 text-sm text-red-600">{errors.meeting_length.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="maxUses" className="block text-sm font-medium text-gray-700">
          Maximum Uses (optional)
        </label>
        <input
          type="number"
          id="maxUses"
          {...register('maxUses')}
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          disabled={isSubmitting}
        />
      </div>

      <div>
        <label htmlFor="expirationDate" className="block text-sm font-medium text-gray-700">
          Expiration Date (optional)
        </label>
        <input
          type="date"
          id="expirationDate"
          {...register('expirationDate')}
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          disabled={isSubmitting}
        />
      </div>

      <div>
        <label htmlFor="maxDaysAhead" className="block text-sm font-medium text-gray-700">
          Maximum Days in Advance
        </label>
        <input
          type="number"
          id="maxDaysAhead"
          {...register('maxDaysAhead', { 
            required: 'Maximum days ahead is required',
            min: { value: 1, message: 'Minimum is 1 day' },
            max: { value: 365, message: 'Maximum is 365 days' }
          })}
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          disabled={isSubmitting}
        />
        {errors.maxDaysAhead && (
          <p className="mt-1 text-sm text-red-600">{errors.maxDaysAhead.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Custom Questions
        </label>
        <div className="mt-2 space-y-4">
          {fields.map((field, index) => (
            <div key={field.id} className="flex items-start space-x-4">
              <div className="flex-grow">
                <input
                  {...register(`custom_questions.${index}.question`)}
                  placeholder="Enter your question"
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  disabled={isSubmitting}
                />
              </div>
              <div className="flex items-center space-x-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    {...register(`custom_questions.${index}.required`)}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    disabled={isSubmitting}
                  />
                  <span className="ml-2 text-sm text-gray-600">Required</span>
                </label>
                <button
                  type="button"
                  onClick={() => remove(index)}
                  className="text-gray-400 hover:text-gray-500"
                  disabled={isSubmitting}
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          ))}
          <button
            type="button"
            onClick={addQuestion}
            className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            disabled={isSubmitting}
          >
            Add Question
          </button>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isSubmitting}
          className="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Creating...' : 'Create Link'}
        </button>
      </div>
    </form>
  );
}

export default CreateLinkForm; 