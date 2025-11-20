import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function ChatPage({ language, setLanguage }) {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [feedbackModal, setFeedbackModal] = useState(null); // {messageId, content}
  const navigate = useNavigate();

  // Check for token on component mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/');
      return;
    }

    // Initialize language from localStorage or URL params
    const localLang = localStorage.getItem('language');
    if (localLang) {
      setLanguage(localLang);
    }

    const urlParams = new URLSearchParams(window.location.search);
    const langParam = urlParams.get('lang');
    if (langParam && (langParam === 'en' || langParam === 'hi')) {
      setLanguage(langParam);
      localStorage.setItem('language', langParam);
    }
  }, [setLanguage, navigate]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/');
      return;
    }

    const userMessage = { role: 'user', content: inputMessage };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: inputMessage,
          language: language
        })
      });

      if (response.ok) {
        const data = await response.json();
        const botMessage = { role: 'assistant', content: data.reply, messageId: data.message_id };
        setMessages(prev => [...prev, botMessage]);
      } else {
        const errorMessage = {
          role: 'assistant',
          content: language === 'en' ? 'Sorry, I couldn\'t process your message.' : 'क्षमा करें, मैं आपका संदेश प्रोसेस नहीं कर सका।'
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: language === 'en' ? 'Connection error. Please try again.' : 'कनेक्शन त्रुटि। कृपया पुनः प्रयास करें।'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const quickMessages = [
    language === 'en' ? "I have a fever and cough" : "मुझे बुखार और खांसी है",
    language === 'en' ? "Give me a wellness tip" : "मुझे एक स्वास्थ्य सलाह दें",
    language === 'en' ? "How to bandage a cut" : "घाव को कैसे बाँधें"
  ];

  const submitFeedback = async (messageId, feedbackType, comment = "") => {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      await fetch('http://localhost:8000/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message_id: messageId,
          feedback_type: feedbackType,
          feedback_comment: comment
        })
      });
      setFeedbackModal(null);
    } catch (error) {
      console.error('Feedback submission failed:', error);
    }
  };

  return (
    <div className="bg-white shadow-lg rounded-2xl p-8 w-full max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-primary flex items-center">
          💬 {language === "en" ? "WellBot Chat" : "वेलबॉट चैट"}
        </h2>

        <div className="flex gap-2">
          <button
            onClick={() => {
              setLanguage("en");
              localStorage.setItem('language', "en");
            }}
            className={`px-3 py-1 rounded-md text-sm ${
              language === "en"
                ? "border-2 border-primary text-primary"
                : "border border-gray-300 text-gray-700"
            }`}
          >
            🇬🇧 EN
          </button>
          <button
            onClick={() => {
              setLanguage("hi");
              localStorage.setItem('language', "hi");
            }}
            className={`px-3 py-1 rounded-md text-sm ${
              language === "hi"
                ? "border-2 border-primary text-primary"
                : "border border-gray-300 text-gray-700"
            }`}
          >
            🇮🇳 HI
          </button>
        </div>
      </div>

      {/* Quick Messages */}
      <div className="mb-4">
        <h3 className="text-sm font-medium text-gray-600 mb-2">
          {language === "en" ? "Quick Messages:" : "त्वरित संदेश:"}
        </h3>
        <div className="flex flex-wrap gap-2">
          {quickMessages.map((msg, index) => (
            <button
              key={index}
              onClick={() => setInputMessage(msg)}
              className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition"
            >
              {msg}
            </button>
          ))}
        </div>
      </div>

      {/* Chat Messages */}
      <div className="bg-gray-50 rounded-lg p-4 mb-4 h-96 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500">
            {language === "en"
              ? "👋 Hello! I'm WellBot. How can I help you with your wellness today?"
              : "👋 नमस्ते! मैं वेलबॉट हूं। आज आपकी सेहत के साथ मैं आपकी कैसे मदद कर सकता हूं?"
            }
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`mb-3 ${
                msg.role === 'user' ? 'text-right' : 'text-left'
              }`}
            >
              <div className="relative">
                <div
                  className={`inline-block px-3 py-2 rounded-lg max-w-xs lg:max-w-md ${
                    msg.role === 'user'
                      ? 'bg-primary text-white'
                      : 'bg-white border border-gray-200 text-gray-800'
                  }`}
                >
                  {msg.content}
                </div>
                {msg.role === 'assistant' && msg.messageId && (
                  <div className="flex gap-1 mt-1">
                    <button
                      onClick={() => submitFeedback(msg.messageId, 'positive')}
                      className="text-green-500 hover:text-green-700 text-sm"
                      title={language === 'en' ? 'Helpful' : 'सहायक'}
                    >
                      👍
                    </button>
                    <button
                      onClick={() => submitFeedback(msg.messageId, 'negative')}
                      className="text-red-500 hover:text-red-700 text-sm"
                      title={language === 'en' ? 'Not helpful' : 'सहायक नहीं'}
                    >
                      👎
                    </button>
                    <button
                      onClick={() => setFeedbackModal({ messageId: msg.messageId, content: msg.content })}
                      className="text-blue-500 hover:text-blue-700 text-sm"
                      title={language === 'en' ? 'Add comment' : 'टिप्पणी जोड़ें'}
                    >
                      💬
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="text-left mb-3">
            <div className="inline-block px-3 py-2 rounded-lg bg-white border border-gray-200 text-gray-800">
              {language === "en" ? "Typing..." : "टाइप कर रहा हूं..."}
            </div>
          </div>
        )}
      </div>

      {/* Message Input */}
      <form onSubmit={sendMessage} className="flex gap-2">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder={language === "en" ? "Type your message..." : "अपना संदेश टाइप करें..."}
          className="flex-1 p-2 border border-gray-300 rounded-md"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !inputMessage.trim()}
          className="bg-gradient-to-r from-teal-600 to-emerald-600 hover:opacity-90 disabled:opacity-50 text-white px-4 py-2 rounded-lg font-medium transition"
        >
          {language === "en" ? "Send" : "भेजें"}
        </button>
      </form>

      {/* Navigation */}
      <div className="mt-4 flex justify-center gap-4">
        <button
          onClick={() => navigate('/profile')}
          className="text-primary hover:underline text-sm"
        >
          {language === "en" ? "Go to Profile" : "प्रोफ़ाइल पर जाएं"}
        </button>
        <button
          onClick={() => {
            localStorage.removeItem('token');
            navigate('/');
          }}
          className="text-red-500 hover:underline text-sm"
        >
          {language === "en" ? "Logout" : "लॉगआउट"}
        </button>
      </div>

      {/* Feedback Modal */}
      {feedbackModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">
              {language === 'en' ? 'Add Feedback Comment' : 'प्रतिक्रिया टिप्पणी जोड़ें'}
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              {language === 'en' ? 'Response:' : 'उत्तर:'} {feedbackModal.content.substring(0, 100)}...
            </p>
            <textarea
              id="feedback-comment"
              className="w-full p-2 border border-gray-300 rounded-md mb-4"
              placeholder={language === 'en' ? 'Your comment (optional)' : 'आपकी टिप्पणी (वैकल्पिक)'}
              rows="3"
            />
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setFeedbackModal(null)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                {language === 'en' ? 'Cancel' : 'रद्द करें'}
              </button>
              <button
                onClick={() => {
                  const comment = document.getElementById('feedback-comment').value;
                  submitFeedback(feedbackModal.messageId, 'comment', comment);
                }}
                className="px-4 py-2 bg-primary text-white rounded-md hover:opacity-90"
              >
                {language === 'en' ? 'Submit' : 'जमा करें'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}