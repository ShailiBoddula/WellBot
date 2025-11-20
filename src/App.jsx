import { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import AuthPage from "./pages/AuthPage";
import ProfilePage from "./pages/ProfilePage";
import ChatPage from "./pages/ChatPage";
import AdminDashboard from "./pages/AdminDashboard";

export default function App() {
  const [language, setLanguage] = useState(() => {
    // Get language from localStorage or default to English
    return localStorage.getItem('language') || "en";
  });

  // Update localStorage when language changes
  const handleLanguageChange = (newLanguage) => {
    setLanguage(newLanguage);
    localStorage.setItem('language', newLanguage);
  };

  return (
    <Router>
      <div className="flex flex-col min-h-screen bg-gray-900 text-white">
        <nav className="bg-gray-800 shadow-md py-4">
          <div className="max-w-5xl mx-auto px-4 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <img src="/src/assets/wellbot-logo.svg" alt="WellBot Logo" className="w-8 h-8"/>
              <h1 className="text-2xl font-bold text-blue-400 tracking-wide">WellBot</h1>
            </div>

            <div className="space-x-6">
              <Link to="/" className="text-gray-300 hover:text-blue-400 font-medium transition">
                {language === "en" ? "User Authentication" : "उपयोगकर्ता प्रमाणीकरण"}
              </Link>
              <Link to="/chat" className="text-gray-300 hover:text-blue-400 font-medium transition">
                {language === "en" ? "Chat" : "चैट"}
              </Link>
              <Link to="/profile" className="text-gray-300 hover:text-blue-400 font-medium transition">
                {language === "en" ? "Profile Management" : "प्रोफ़ाइल प्रबंधन"}
              </Link>
              <Link to="/dashboard" className="text-gray-300 hover:text-blue-400 font-medium transition">
                {language === "en" ? "Dashboard" : "डैशबोर्ड"}
              </Link>
            </div>
          </div>
        </nav>

        <main className="flex-grow w-full bg-gray-900 px-6 py-6 overflow-y-auto">
          <Routes>
            <Route path="/" element={<AuthPage language={language} setLanguage={handleLanguageChange} />} />
            <Route path="/chat" element={<ChatPage language={language} setLanguage={handleLanguageChange} />} />
            <Route path="/profile" element={<ProfilePage language={language} setLanguage={handleLanguageChange} />} />
            <Route path="/dashboard" element={<AdminDashboard />} />
          </Routes>
        </main>

        <footer className="text-center py-4 text-gray-400 text-sm bg-gray-800">
          © 2025 Well Bot
        </footer>
      </div>
    </Router>
  );
}
