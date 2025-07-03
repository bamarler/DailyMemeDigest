import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const NewsPreferences = () => {
  const [preferences, setPreferences] = useState({
    openai: true,
    claude: true,
    machineLearning: true,
    generativeAI: true,
    robotics: false,
    autonomous: false,
    neuralNetworks: false,
    deepLearning: false,
    aiEthics: false,
    aiSafety: false
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user has email from previous page
    const userEmail = localStorage.getItem('userEmail');
    if (!userEmail) {
      navigate('/');
    }
  }, [navigate]);

  const handleToggle = (category) => {
    setPreferences(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const handleDone = async () => {
    setIsLoading(true);
    setError('');

    try {
      const userEmail = localStorage.getItem('userEmail');
      
      // Update user preferences and send confirmation email
      const response = await axios.post('/api/preferences', {
        email: userEmail,
        preferences: preferences
      });

      if (response.data.success) {
        navigate('/confirmation-sent');
      } else {
        setError(response.data.error || 'Failed to save preferences. Please try again.');
      }
    } catch (err) {
      console.error('Preferences error:', err);
      setError('Failed to save preferences. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const categories = [
    { key: 'openai', label: 'OpenAI & ChatGPT', description: 'Latest updates from OpenAI and ChatGPT developments' },
    { key: 'claude', label: 'Claude & Anthropic', description: 'News about Claude AI and Anthropic\'s research' },
    { key: 'machineLearning', label: 'Machine Learning', description: 'General machine learning breakthroughs and research' },
    { key: 'generativeAI', label: 'Generative AI', description: 'Text, image, and video generation technologies' },
    { key: 'robotics', label: 'Robotics & Automation', description: 'AI-powered robots and automation systems' },
    { key: 'autonomous', label: 'Autonomous Systems', description: 'Self-driving cars, drones, and autonomous vehicles' },
    { key: 'neuralNetworks', label: 'Neural Networks', description: 'Deep learning and neural network architectures' },
    { key: 'deepLearning', label: 'Deep Learning', description: 'Advanced deep learning techniques and applications' },
    { key: 'aiEthics', label: 'AI Ethics & Policy', description: 'Ethical considerations and policy discussions around AI' },
    { key: 'aiSafety', label: 'AI Safety & Alignment', description: 'AI safety research and alignment efforts' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-2xl mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Choose Your News Preferences
          </h1>
          <p className="text-gray-600">
            Select which AI topics you'd like to receive updates about
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="space-y-4">
            {categories.map((category) => (
              <div key={category.key} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{category.label}</h3>
                  <p className="text-sm text-gray-500">{category.description}</p>
                </div>
                <button
                  onClick={() => handleToggle(category.key)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    preferences[category.key] ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      preferences[category.key] ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            ))}

            {error && (
              <div className="text-red-600 text-sm text-center">
                {error}
              </div>
            )}

            <button
              onClick={handleDone}
              disabled={isLoading}
              className={`w-full py-3 px-4 rounded-md font-medium transition-colors ${
                isLoading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {isLoading ? 'Saving...' : 'Done'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewsPreferences; 