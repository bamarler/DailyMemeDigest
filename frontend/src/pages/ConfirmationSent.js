import React from 'react';
import { useNavigate } from 'react-router-dom';

const ConfirmationSent = () => {
  const navigate = useNavigate();

  const handleContinue = () => {
    console.log('🚀 Continuing to thank you page');
    navigate('/thank-you');
  };

  // Debug: Log the stored email
  React.useEffect(() => {
    const storedEmail = localStorage.getItem('userEmail');
    console.log('📧 Stored email from localStorage:', storedEmail);
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
            <svg
              className="h-6 w-6 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Successfully Subscribed!
          </h1>
          
          <div className="bg-white rounded-lg shadow-lg p-6 text-left">
            <p className="text-gray-600 mb-4">
              Thank you for subscribing to our AI Meme Newsletter! You're all set to receive:
            </p>
            
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>Daily AI-generated memes based on trending news</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>Hilarious takes on the latest tech and AI developments</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>Direct links to the original articles</span>
              </li>
            </ul>
            
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Your first newsletter will arrive soon!</strong> Keep an eye on your inbox for the latest AI memes delivered via MailerLite.
              </p>
            </div>
          </div>
          
          <button
            onClick={handleContinue}
            className="mt-6 w-full bg-blue-600 text-white py-3 px-4 rounded-md font-medium hover:bg-blue-700 transition-colors"
          >
            Continue to Thank You Page
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationSent; 