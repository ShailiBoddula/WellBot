import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

export default function AuthPage({ language, setLanguage }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(null);
  const [error, setError] = useState("");

  // Initialize language from localStorage first, then URL params
  useEffect(() => {
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
  }, [setLanguage]);

  const handleLogin = async (e) => {
    e.preventDefault();
    console.log('=== LOGIN ATTEMPT START ===');
    console.log('Login button clicked, email:', email, 'password:', password); // Debug log
    console.log('Email length:', email.length, 'Password length:', password.length);
    setError("");

    if (!email || !password) {
      console.log('Validation failed: missing email or password');
      setError("Please enter both email and password");
      return;
    }

    console.log('Validation passed, proceeding with login...');

    try {
      console.log('Making login request to http://localhost:8000/auth/login...');
      console.log('Request body:', JSON.stringify({ email, password }));

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout

      const response = await fetch('http://127.0.0.1:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));

      if (response.ok) {
        const data = await response.json();
        console.log('Login successful! Response data:', data);
        console.log('Token received:', data.token ? 'YES' : 'NO');

        setToken(data.token);
        localStorage.setItem('token', data.token);

        // Sign In goes directly to Streamlit chat with token
        console.log('Redirecting to Streamlit chat...');
        const redirectUrl = `http://127.0.0.1:8501/?token=${encodeURIComponent(data.token)}&lang=${language}`;
        console.log('Redirect URL:', redirectUrl);

        // Instant redirect - update profile in background
        window.location.href = redirectUrl;

        // Update language in profile asynchronously (non-blocking)
        fetch('http://127.0.0.1:8000/profile', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${data.token}`
          },
          body: JSON.stringify({ language: language })
        }).catch(langError => console.log('Language update failed:', langError));
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.log('Login failed with status:', response.status, 'Error data:', errorData);
        setError(errorData.error || "Invalid credentials");
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        console.error('Login request timed out after 30 seconds');
        setError("Login request timed out - check if backend is running");
      } else {
        console.error('Login error details:', error);
        console.error('Error name:', error.name);
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
        setError("Login failed - check if backend is running");
      }
    }

    console.log('=== LOGIN ATTEMPT END ===');
  };

  const navigate = useNavigate();

  return (
    <div className="bg-gray-800 shadow-lg rounded-2xl p-8 w-full max-w-md border border-gray-700 mx-auto">
      <h2 className="text-xl font-semibold text-blue-400 mb-4 flex items-center">
        🔒 {language === "en" ? "User Authentication" : "उपयोगकर्ता प्रमाणीकरण"}
      </h2>

      <div className="flex gap-2 mb-4">
        <button
          type="button"
          onClick={() => setLanguage("en")}
          className={`flex-1 py-2 rounded-md border-2 transition ${
            language === "en"
              ? "border-blue-400 text-blue-400 bg-blue-900/20"
              : "border-gray-600 text-gray-400 hover:border-gray-500"
          }`}
        >
          🇬🇧 English
        </button>
        <button
          type="button"
          onClick={() => setLanguage("hi")}
          className={`flex-1 py-2 rounded-md border-2 transition ${
            language === "hi"
              ? "border-blue-400 text-blue-400 bg-blue-900/20"
              : "border-gray-600 text-gray-400 hover:border-gray-500"
          }`}
        >
          🇮🇳 हिंदी
        </button>
      </div>

      {error && <div className="text-red-400 text-sm mb-4">{error}</div>}

      <form className="space-y-4" onSubmit={handleLogin}>
        <div>
          <label className="block mb-2 text-sm font-medium text-gray-300">
            {language === "en" ? "Email" : "ईमेल"}
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder={language === "en" ? "user@example.com" : "उपयोगकर्ता@उदाहरण.com"}
            className="w-full p-2 border border-gray-600 rounded-md bg-gray-700 text-white placeholder-gray-400 focus:border-blue-400 focus:outline-none"
            required
          />
        </div>

        <div>
          <label className="block mb-2 text-sm font-medium text-gray-300">
            {language === "en" ? "Password" : "पासवर्ड"}
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder={language === "en" ? "••••••••" : "••••••••"}
            className="w-full p-2 border border-gray-600 rounded-md bg-gray-700 text-white placeholder-gray-400 focus:border-blue-400 focus:outline-none"
            required
          />
        </div>

        <div className="flex justify-between items-center text-sm text-gray-400">
          <label>
            <input type="checkbox" className="mr-1" />
            {language === "en" ? "Remember me" : "मुझे याद रखें"}
          </label>
          <a href="#" className="text-blue-400 hover:text-blue-300 hover:underline">
            {language === "en" ? "Forgot password?" : "पासवर्ड भूल गए?"}
          </a>
        </div>

        <button
          type="submit"
          className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-2 rounded-lg font-medium transition"
        >
          {language === "en" ? "Sign In" : "साइन इन करें"}
        </button>

        <button
          type="button"
          className="w-full border-2 border-blue-600 text-blue-400 py-2 rounded-lg font-medium transition hover:bg-blue-900/20"
          onClick={async () => {
            // Create account by attempting login (backend auto-creates)
            try {
              const response = await fetch('http://127.0.0.1:8000/auth/login', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
              });
              if (response.ok) {
                const data = await response.json();
                localStorage.setItem('token', data.token);

                // ✅ Pass token to profile
                navigate(`/profile?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}&token=${encodeURIComponent(data.token)}&lang=${language}`);
              } else {
                setError("Account creation failed");
              }
            } catch (error) {
              setError("Account creation failed");
            }
          }}
        >
          {language === "en" ? "Create Account" : "खाता बनाएँ"}
        </button>
      </form>
    </div>
  );
}
