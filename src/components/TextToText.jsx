import React, { useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

function TextToText() {
  const { user } = useAuth();

  useEffect(() => {
    // Open Streamlit in an iframe when component mounts
    const iframe = document.createElement('iframe');
    iframe.src = 'http://localhost:8501';
    iframe.style.width = '100%';
    iframe.style.height = '800px';
    iframe.style.border = 'none';
    document.getElementById('streamlit-container').appendChild(iframe);

    // Post user data to Streamlit
    iframe.onload = () => {
      iframe.contentWindow.postMessage({
        type: 'streamlit:setSessionState',
        state: {
          student_username: user.username,
          student_logged_in: true
        }
      }, '*');
    };

    return () => {
      document.getElementById('streamlit-container').removeChild(iframe);
    };
  }, [user]);

  return (
    <div id="streamlit-container" className="w-full h-full">
      <div className="text-center py-4">
        <h2 className="text-2xl font-bold text-gray-900">Text-to-Text Assessment</h2>
        <p className="text-gray-600">Loading assessment module...</p>
      </div>
    </div>
  );
}

export default TextToText;