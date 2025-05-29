import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import TextToText from '../components/TextToText';
import VoiceToVoice from '../components/VoiceToVoice';
import FaceToFace from '../components/FaceToFace';

function Dashboard() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <img
                  className="h-8 w-auto"
                  src="https://growthmateinfotech.in/growthmate/assets/img/logo1.png"
                  alt="Growthmate"
                />
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link
                  to="/dashboard"
                  className="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  Dashboard
                </Link>
              </div>
            </div>
            <div className="flex items-center">
              <button
                onClick={logout}
                className="ml-8 whitespace-nowrap inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-base font-medium text-white bg-indigo-600 hover:bg-indigo-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {/* Token Cards */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <dt className="text-sm font-medium text-gray-500">Text-to-Text Tokens</dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">
                  {user?.ai_tokens?.Text_to_Text || 15}
                </dd>
              </div>
            </div>
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <dt className="text-sm font-medium text-gray-500">Voice-to-Voice Tokens</dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">
                  {user?.ai_tokens?.Voice_to_Voice || 15}
                </dd>
              </div>
            </div>
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <dt className="text-sm font-medium text-gray-500">Face-to-Face Tokens</dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">
                  {user?.ai_tokens?.Face_to_Face || 15}
                </dd>
              </div>
            </div>
          </div>

          <div className="mt-8">
            <Routes>
              <Route path="/" element={<ModuleSelection />} />
              <Route path="/text-to-text" element={<TextToText />} />
              <Route path="/voice-to-voice" element={<VoiceToVoice />} />
              <Route path="/face-to-face" element={<FaceToFace />} />
            </Routes>
          </div>
        </div>
      </div>
    </div>
  );
}

function ModuleSelection() {
  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <Link
        to="/dashboard/text-to-text"
        className="block p-6 bg-white rounded-lg shadow hover:shadow-lg transition-shadow"
      >
        <h3 className="text-lg font-medium text-gray-900">Text-to-Text</h3>
        <p className="mt-2 text-sm text-gray-500">
          Interactive text-based assessments and feedback
        </p>
      </Link>
      <Link
        to="/dashboard/voice-to-voice"
        className="block p-6 bg-white rounded-lg shadow hover:shadow-lg transition-shadow"
      >
        <h3 className="text-lg font-medium text-gray-900">Voice-to-Voice</h3>
        <p className="mt-2 text-sm text-gray-500">
          Voice-based interactions and assessments
        </p>
      </Link>
      <Link
        to="/dashboard/face-to-face"
        className="block p-6 bg-white rounded-lg shadow hover:shadow-lg transition-shadow"
      >
        <h3 className="text-lg font-medium text-gray-900">Face-to-Face</h3>
        <p className="mt-2 text-sm text-gray-500">
          Coming soon: Video-based interactions
        </p>
      </Link>
    </div>
  );
}

export default Dashboard;