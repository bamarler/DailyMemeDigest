import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

// Get API configuration from environment variables
const API_URL = process.env.REACT_APP_API_BASE_URL;
const API_KEY = process.env.REACT_APP_NEWSLETTER_API_KEY;
console.log('API_URL:', API_URL);
console.log('API_KEY:', API_KEY ? 'Set' : 'Not set');

const MemeGallery = () => {
  const [memes, setMemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchMemes = async () => {
      const apiUrl = `${API_URL}/memes?limit=100`;
      console.log('🔍 Attempting to fetch memes from:', apiUrl);
      console.log('🔑 Using API key:', API_KEY ? 'Set' : 'Not set');
      
      try {
        console.log('📡 Making API request...');
        const response = await axios.get(apiUrl, {
          headers: {
            'X-API-Key': API_KEY
          }
        });
        console.log('📊 Response status:', response.status);
        console.log('📄 Response data:', response.data);
        
        if (response.data.success) {
          console.log('✅ Success! Found', response.data.memes?.length || 0, 'memes');
          setMemes(response.data.memes || []);
        } else {
          console.log('❌ API returned success: false');
          console.log('❌ Error details:', response.data);
          setError(`Failed to load memes: ${response.data.error || 'Unknown error'}`);
        }
      } catch (err) {
        console.error('💥 Error fetching memes:', err);
        console.error('💥 Error details:', {
          message: err.message,
          status: err.response?.status,
          statusText: err.response?.statusText,
          data: err.response?.data
        });
        
        if (err.response) {
          // Server responded with error status
          setError(`Server error: ${err.response.status} - ${err.response.statusText}`);
        } else if (err.request) {
          // Request was made but no response
          setError('No response from server. Check if API is running.');
        } else {
          // Something else happened
          setError(`Network error: ${err.message}`);
        }
      } finally {
        console.log('🏁 Finished loading attempt');
        setLoading(false);
      }
    };

    fetchMemes();
  }, []);

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p className="text-gray-600 mt-2">Loading recent memes...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-2">Unable to load recent memes</p>
        <p className="text-sm text-gray-500">Error: {error}</p>
        <button 
          onClick={() => window.location.reload()} 
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="mt-12">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
        Some of our work
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {memes.map((meme, index) => (
          <div key={index} className="group">
            <a 
              href={meme.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="block transition-transform duration-200 hover:scale-105"
            >
              <div className="bg-white rounded-lg shadow-md overflow-hidden">
                <img 
                  src={meme.image} 
                  alt="AI Generated Meme" 
                  className="w-full h-48 object-cover"
                  onError={(e) => {
                    console.log('🖼️ Image failed to load:', meme.image);
                    e.target.src = 'https://via.placeholder.com/300x200?text=Meme+Loading...';
                  }}
                />
                <div className="p-3">
                  <p className="text-xs text-gray-500 truncate">
                    Click to read article
                  </p>
                </div>
              </div>
            </a>
          </div>
        ))}
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
      
      // Add email to Mailchimp list
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
              AI Meme Newsletter
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