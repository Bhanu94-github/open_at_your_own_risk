import React, { useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

function VoiceToVoice() {
  const { user } = useAuth();

  useEffect(() => {
    const iframe = document.createElement('iframe');
    iframe.src = 'http://localhost:8501/voice';
    iframe.style.width = '100%';
    iframe.style.height = '800px';
    iframe.style.border = 'none';
    document.getElementById('voice-container').appendChild(iframe);

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
      document.getElementById('voice-container').removeChild(iframe);
    };
  }, [user]);

  return (
    <div id="voice-container" className="w-full h-full">
      <div className="text-center py-4">
        <h2 className="text-2xl font-bold text-gray-900">Voice-to-Voice Assessment</h2>
        <p className="text-gray-600">Loading voice module...</p>
      </div>
    </div>
  );
}

export default VoiceToVoice;