import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const EmailSignup = () => {
  const [email, setEmail] = useState('');
  const [isValid, setIsValid] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleEmailChange = (e) => {
    const newEmail = e.target.value;
    setEmail(newEmail);
    setIsValid(validateEmail(newEmail));
    setError('');
  };

  const handleSubscribe = async () => {
    if (!isValid) return;

    setIsLoading(true);
    setError('');

    try {
      // Add email to Mailchimp list
      const response = await axios.post('/api/subscribe', {
        email: email
      });

      if (response.data.success) {
        // Store email in localStorage for next page
        localStorage.setItem('userEmail', email);
        navigate('/preferences');
      } else {
        setError(response.data.error || 'Failed to subscribe. Please try again.');
      }
    } catch (err) {
      console.error('Subscription error:', err);
      setError('Failed to subscribe. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            AI Meme Newsletter
          </h1>
          <p className="text-gray-600">
            Stay updated with the latest AI trends and hilarious memes
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={handleEmailChange}
                placeholder="Enter your email address"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {error && (
              <div className="text-red-600 text-sm">
                {error}
              </div>
            )}

            <button
              onClick={handleSubscribe}
              disabled={!isValid || isLoading}
              className={`w-full py-2 px-4 rounded-md font-medium transition-colors ${
                isValid && !isLoading
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              {isLoading ? 'Subscribing...' : 'Subscribe'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailSignup; 