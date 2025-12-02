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
  const [memes, setMemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState('');
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [flippedMemes, setFlippedMemes] = useState(new Set());
  
  const loadingRef = useRef(null);
  
  const MEMES_PER_PAGE = 32;

  const toggleFlip = (memeIndex) => {
    setFlippedMemes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(memeIndex)) {
        newSet.delete(memeIndex);
      } else {
        newSet.add(memeIndex);
      }
      return newSet;
    });
  };

  const formatDateTime = (dateString, meme, index) => {
    console.log(`🗓️ Meme ${index} - formatDateTime called with:`, dateString);
    console.log(`🗓️ Meme ${index} - type of dateString:`, typeof dateString);
    console.log(`🗓️ Meme ${index} - created_at field specifically:`, meme.created_at);
    console.log(`🗓️ Meme ${index} - full meme object keys:`, Object.keys(meme));
    console.log(`🗓️ Meme ${index} - DETAILED meme object keys and values:`);
    Object.keys(meme).forEach(key => {
      console.log(`  🔑 ${key}:`, meme[key], `(type: ${typeof meme[key]})`);
    });
    console.log(`🗓️ Meme ${index} - full meme object:`, meme);
    
    const possibleDateFields = [
      'created_at', 'date_generated', 'timestamp', 'date', 'created', 
      'generated', 'generation_time', 'created_date', 'publish_date',
      'updated_at', 'time', 'datetime'
    ];
    
    console.log(`🔍 Meme ${index} - Checking all possible date fields:`);
    possibleDateFields.forEach(field => {
      if (meme[field] !== undefined) {
        console.log(`  ✅ Found date field "${field}":`, meme[field]);
      }
    });
    
    if (!dateString) {
      console.log(`❌ Meme ${index} - No date string provided (null/undefined/empty)`);
      return 'Date not available';
    }
    
    try {
      console.log(`🔧 Meme ${index} - Processing date string:`, dateString);
      
      let cleanDateString = dateString;
      
      if (dateString.includes('.') && dateString.split('.')[1].length > 3) {
        console.log(`🔧 Meme ${index} - Found microseconds, truncating...`);
        const parts = dateString.split('.');
        const beforeDecimal = parts[0];
        const afterDecimal = parts[1];
        cleanDateString = beforeDecimal + '.' + afterDecimal.substring(0, 3);
        if (!dateString.includes('Z') && !dateString.includes('+') && !dateString.includes('-', 10)) {
          cleanDateString += 'Z';
        }
        console.log(`🔧 Meme ${index} - Cleaned date string:`, cleanDateString);
      }
      
      const date = new Date(cleanDateString);
      console.log(`🔧 Meme ${index} - Created Date object:`, date);
      console.log(`🔧 Meme ${index} - Date.getTime():`, date.getTime());
      
      if (isNaN(date.getTime())) {
        console.log(`❌ Meme ${index} - Invalid date string:`, dateString);
        return 'Invalid date format';
      }
      
      const formatted = date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });
      
      console.log(`✅ Meme ${index} - Successfully formatted date:`, formatted);
      return formatted;
    } catch (error) {
      console.log(`💥 Meme ${index} - Date parsing error:`, error, 'for string:', dateString);
      return 'Date parsing error';
    }
  };

  const fetchMemes = useCallback(async (currentOffset = 0, isLoadMore = false) => {
    const apiUrl = `${API_URL}/memes?limit=${MEMES_PER_PAGE}&offset=${currentOffset}`;
    console.log('🔍 Attempting to fetch memes from:', apiUrl);
    console.log('🔑 Using API key:', API_KEY ? 'Set' : 'Not set');
    console.log('📍 Offset:', currentOffset, 'Is load more:', isLoadMore);
    
    if (isLoadMore) {
      setLoadingMore(true);
    }
    
    try {
      console.log('📡 Making API request...');
      const response = await axios.get(apiUrl);
      console.log('📊 Response status:', response.status);
      console.log('📄 Response data:', response.data);
      
      if (response.data.success) {
        const newMemes = response.data.memes || [];
        const pagination = response.data.pagination || {};
        
        console.log('✅ Success! Found', newMemes.length, 'memes');
        console.log('📊 Pagination info:', pagination);
        
        if (isLoadMore) {
          setMemes(prevMemes => [...prevMemes, ...newMemes]);
        } else {
          setMemes(newMemes);
        }
        
        setTotalCount(pagination.total_count || 0);
        setOffset(currentOffset + newMemes.length);
        
        const hasMoreMemes = pagination.has_more || 
          (pagination.total_count && (currentOffset + newMemes.length) < pagination.total_count);
        setHasMore(hasMoreMemes);
        
        console.log('📈 Updated state:', {
          totalMemes: isLoadMore ? memes.length + newMemes.length : newMemes.length,
          newOffset: currentOffset + newMemes.length,
          hasMore: hasMoreMemes,
          totalCount: pagination.total_count
        });
        
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
        setError(`Server error: ${err.response.status} - ${err.response.statusText}`);
      } else if (err.request) {
        setError('No response from server. Check if API is running.');
      } else {
        setError(`Network error: ${err.message}`);
      }
    } finally {
      console.log('🏁 Finished loading attempt');
      if (isLoadMore) {
        setLoadingMore(false);
      } else {
        setLoading(false);
      }
    }
  }, [API_URL, API_KEY, memes.length]);

  const loadMoreMemes = useCallback(() => {
    if (!loadingMore && hasMore && !loading) {
      console.log('🔄 Loading more memes with offset:', offset);
      fetchMemes(offset, true);
    }
  }, [offset, hasMore, loadingMore, loading, fetchMemes]);

  useEffect(() => {
    fetchMemes(0, false);
  }, []);

  useEffect(() => {
    const currentLoadingRef = loadingRef.current;
    
    if (!currentLoadingRef || !hasMore || loading) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting && hasMore && !loadingMore) {
          console.log('👁️ Loading indicator visible, triggering load more');
          loadMoreMemes();
        }
      },
      {
        threshold: 0.1,
        rootMargin: '100px'
      }
    );

    observer.observe(currentLoadingRef);

    return () => {
      if (currentLoadingRef) {
        observer.unobserve(currentLoadingRef);
      }
    };
  }, [hasMore, loadingMore, loading, loadMoreMemes]);

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p className="text-gray-600 mt-2">Loading recent memes...</p>
      </div>
    );
  }

  if (error && memes.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-2">Unable to load recent memes</p>
        <p className="text-sm text-gray-500">Error: {error}</p>
        <button 
          onClick={() => {
            setError('');
            setOffset(0);
            setHasMore(true);
            fetchMemes(0, false);
          }} 
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

      {/* CHANGED: CSS Columns masonry layout */}
      <style>{`
        .masonry-gallery {
          column-count: 4;
          column-gap: 16px;
        }
        @media (max-width: 1280px) { .masonry-gallery { column-count: 3; } }
        @media (max-width: 900px) { .masonry-gallery { column-count: 2; } }
        @media (max-width: 500px) { .masonry-gallery { column-count: 1; } }
        .masonry-item {
          break-inside: avoid;
          margin-bottom: 16px;
        }
      `}</style>

      <div className="masonry-gallery">
        {memes.map((meme, index) => {
          const isFlipped = flippedMemes.has(index);
          return (
            <div key={`${meme.id || index}-${offset}`} className="masonry-item group relative">
              {/* Flip Card Container - CHANGED: removed fixed h-64 */}
              <div 
                className="relative w-full transition-transform duration-700" 
                style={{ 
                  transformStyle: 'preserve-3d',
                  transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)'
                }}
              >
                
                {/* Front Side - CHANGED: image in normal flow sets height */}
                <div 
                  className="w-full" 
                  style={{ backfaceVisibility: 'hidden' }}
                >
                  <a 
                    href={meme.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="block transition-transform duration-200 hover:scale-105"
                  >
                    <img 
                      src={meme.image} 
                      alt="AI Generated Meme" 
                      className="w-full rounded-lg shadow-md"
                      onError={(e) => {
                        console.log('🖼️ Image failed to load:', meme.image);
                        e.target.src = 'https://via.placeholder.com/300x200?text=Meme+Loading...';
                      }}
                    />
                  </a>
                </div>

                {/* Back Side - CHANGED: absolute to fill container */}
                <div 
                  className="absolute inset-0 w-full h-full" 
                  style={{ 
                    backfaceVisibility: 'hidden',
                    transform: 'rotateY(180deg)' 
                  }}
                >
                  <div className="bg-gradient-to-br from-blue-200 to-blue-400 rounded-lg shadow-md h-full p-4 text-gray-800 flex flex-col">
                    <h3 className="text-sm font-semibold mb-3 text-center flex-shrink-0 text-gray-800">
                      Generation Details
                    </h3>
                    
                    <div className="flex-1 overflow-y-auto min-h-0 space-y-3 pr-1" 
                         style={{ scrollbarWidth: 'thin', scrollbarColor: 'rgba(0,0,0,0.3) transparent' }}>
                      <div>
                        <p className="text-xs font-medium mb-1 text-gray-700">Prompt:</p>
                        <p className="text-xs leading-relaxed break-words text-gray-800">
                          {meme.prompt || 'Prompt not available'}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs font-medium mb-1 text-gray-700">Generated:</p>
                        <p className="text-xs text-gray-800">
                          {formatDateTime(meme.generated_at, meme, index)}
                        </p>
                      </div>
                    </div>
                    
                    <div className="text-center mt-3 flex-shrink-0">
                      <a 
                        href={meme.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-xs underline hover:no-underline text-gray-700 hover:text-gray-900"
                      >
                        View full article
                      </a>
                    </div>
                  </div>
                </div>
              </div>

              {/* Flip Icon */}
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  toggleFlip(index);
                }}
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
          );
        })}
      </div>

      {/* Rest unchanged */}
      {hasMore && (
        <div ref={loadingRef} className="text-center py-8">
          {loadingMore ? (
            <div>
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-600 mt-2 text-sm">Loading more memes...</p>
            </div>
          ) : (
            <div className="h-6"></div>
          )}
        </div>
      )}

      {!hasMore && memes.length > 0 && (
        <div className="text-center py-8">
          <p className="text-gray-500 text-sm">
            🎉 You've seen all {totalCount || memes.length} memes! 
            {totalCount > memes.length && ` (${memes.length} loaded)`}
          </p>
        </div>
      )}

      {error && memes.length > 0 && (
        <div className="text-center py-4">
          <p className="text-red-600 text-sm mb-2">Failed to load more memes</p>
          <button 
            onClick={() => {
              setError('');
              loadMoreMemes();
            }}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      )}
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