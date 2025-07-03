import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import EmailSignup from './pages/EmailSignup';
import NewsPreferences from './pages/NewsPreferences';
import ConfirmationSent from './pages/ConfirmationSent';
import ThankYou from './pages/ThankYou';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<EmailSignup />} />
          <Route path="/preferences" element={<NewsPreferences />} />
          <Route path="/confirmation-sent" element={<ConfirmationSent />} />
          <Route path="/thank-you" element={<ThankYou />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 