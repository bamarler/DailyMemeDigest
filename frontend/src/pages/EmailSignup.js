import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { RotateCcw } from 'lucide-react';
import axios from 'axios';

// Get API configuration from environment variables
const API_URL = process.env.REACT_APP_API_BASE_URL || '';
const API_KEY = process.env.REACT_APP_NEWSLETTER_API_KEY;
console.log('API_URL:', API_URL);
console.log('API_KEY:', API_KEY ? 'Set' : 'Not set');

const MemeGallery = () => {
  const [memes] = useState(mockMemes);
  const [flippedMemes, setFlippedMemes] = useState(new Set());

  const toggleFlip = (memeId) => {
    setFlippedMemes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(memeId)) {
        newSet.delete(memeId);
      } else {
        newSet.add(memeId);
      }
      return newSet;
    });
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'Date not available';
    try {
      let clean = dateString;
      if (dateString.includes('.') && dateString.split('.')[1]?.length > 3) {
        const [before, after] = dateString.split('.');
        clean = before + '.' + after.substring(0, 3) + 'Z';
      }
      const date = new Date(clean);
      if (isNaN(date.getTime())) return 'Invalid date';
      return date.toLocaleString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit', hour12: true
      });
    } catch {
      return 'Date error';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
        Some of our work
      </h2>

      {/* Masonry layout using CSS columns */}
      <div 
        className="mx-auto"
        style={{
          columnCount: 4,
          columnGap: '16px',
          maxWidth: '1400px',
        }}
      >
        <style>{`
          @media (max-width: 1280px) { .masonry-container { column-count: 3 !important; } }
          @media (max-width: 900px) { .masonry-container { column-count: 2 !important; } }
          @media (max-width: 500px) { .masonry-container { column-count: 1 !important; } }
        `}</style>
        
        <div className="masonry-container" style={{ columnCount: 'inherit', columnGap: 'inherit' }}>
          {memes.map((meme) => {
            const isFlipped = flippedMemes.has(meme.id);
            return (
              <div 
                key={meme.id} 
                style={{ 
                  breakInside: 'avoid',
                  marginBottom: '16px',
                }}
              >
                {/* Flip card container */}
                <div 
                  className="relative rounded-lg overflow-hidden shadow-md bg-white"
                  style={{ perspective: '1000px' }}
                >
                  {/* Inner rotating container */}
                  <div
                    className="relative w-full transition-transform duration-700"
                    style={{
                      transformStyle: 'preserve-3d',
                      transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
                    }}
                  >
                    {/* Front - Image in normal flow sets the height */}
                    <div style={{ backfaceVisibility: 'hidden' }}>
                      <img
                        src={meme.image}
                        alt="AI Generated Meme"
                        className="w-full block rounded-lg"
                        style={{ display: 'block' }}
                        onError={(e) => {
                          e.target.src = 'https://picsum.photos/400/300';
                        }}
                      />
                    </div>

                    {/* Back - Absolute positioned, fills container */}
                    <div
                      className="absolute inset-0 w-full h-full"
                      style={{
                        backfaceVisibility: 'hidden',
                        transform: 'rotateY(180deg)',
                      }}
                    >
                      <div className="bg-gradient-to-br from-blue-200 to-blue-400 rounded-lg h-full p-4 text-gray-800 flex flex-col">
                        <h3 className="text-sm font-semibold mb-3 text-center text-gray-800">
                          Generation Details
                        </h3>
                        
                        <div className="flex-1 overflow-y-auto min-h-0 space-y-3 pr-1">
                          <div>
                            <p className="text-xs font-medium mb-1 text-gray-700">Prompt:</p>
                            <p className="text-xs leading-relaxed break-words text-gray-800">
                              {meme.prompt || 'Prompt not available'}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs font-medium mb-1 text-gray-700">Generated:</p>
                            <p className="text-xs text-gray-800">
                              {formatDateTime(meme.generated_at)}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Flip button */}
                  <button
                    onClick={() => toggleFlip(meme.id)}
                    className="absolute top-2 right-2 z-10 bg-white bg-opacity-90 hover:bg-opacity-100 
                              rounded-full p-2 shadow-md transition-all duration-200 
                              hover:scale-110 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    title={isFlipped ? "Show meme" : "Show details"}
                  >
                    <RotateCcw
                      size={16}
                      className={`text-gray-700 transition-transform duration-300 ${
                        isFlipped ? 'rotate-180' : ''
                      }`}
                    />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

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
      console.log('🔍 Attempting to subscribe email:', email);
      
      // Add email to Brevo list
      const response = await axios.post('/api/subscribe', {
        email: email
      });

      console.log('📡 API Response:', response.data);

      if (response.data.success) {
        console.log('✅ Subscription successful, navigating to confirmation');
        // Store email in localStorage for next page
        localStorage.setItem('userEmail', email);
        navigate('/confirmation-sent');
      } else {
        console.log('❌ Subscription failed:', response.data.error);
        setError(response.data.error || 'Failed to subscribe. Please try again.');
      }
    } catch (err) {
      console.error('💥 Subscription error:', err);
      console.error('💥 Error details:', {
        message: err.message,
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data
      });
      setError('Failed to subscribe. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header Section */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Daily Meme Digest
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Stay updated with the latest AI trends and hilarious memes delivered to your inbox daily
            </p>
          </div>

          {/* Signup Form */}
          <div className="max-w-md mx-auto mb-12">
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

          {/* Meme Gallery */}
          <MemeGallery />
        </div>
      </div>
    </div>
  );
};

export default EmailSignup;