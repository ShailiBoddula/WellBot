import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function ProfilePage({ language, setLanguage }) {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [ageGroup, setAgeGroup] = useState("18-25");
  const [profileLoaded, setProfileLoaded] = useState(false);

  useEffect(() => {
    const savedName = localStorage.getItem("name");
    const savedAgeGroup = localStorage.getItem("ageGroup");
    const savedLang = localStorage.getItem("language") || "en";

    if (savedName) setName(savedName);
    if (savedAgeGroup) setAgeGroup(savedAgeGroup);

    setLanguage(savedLang);
    setProfileLoaded(true);
  }, [setLanguage]);

  if (!profileLoaded) return null;

  const handleSaveAndGo = () => {
    localStorage.setItem("name", name);
    localStorage.setItem("ageGroup", ageGroup);

    const lang = localStorage.getItem("language") || "en";
    const token = localStorage.getItem("token") || "";
    
    window.location.href = `http://127.0.0.1:8501/?token=${encodeURIComponent(token)}&lang=${lang}`;
  };

  return (
    <div className="bg-gray-800 shadow-lg rounded-2xl p-8 w-full max-w-md border border-gray-700 mx-auto">
      <h2 className="text-xl font-semibold text-blue-400 mb-4 flex items-center">
        👤 {language === "en" ? "Profile Management" : "प्रोफ़ाइल प्रबंधन"}
      </h2>

      <div className="space-y-4">
        <div>
          <label className="block mb-2 text-sm font-medium text-gray-300">
            {language === "en" ? "Name" : "नाम"}
          </label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={language === "en" ? "Enter your name" : "अपना नाम दर्ज करें"}
            className="w-full p-2 border border-gray-600 rounded-md bg-gray-700 text-white placeholder-gray-400 focus:border-blue-400 focus:outline-none"
          />
        </div>

        <div>
          <label className="block mb-2 text-sm font-medium text-gray-300">
            {language === "en" ? "Age Group" : "आयु वर्ग"}
          </label>
          <select
            value={ageGroup}
            onChange={(e) => setAgeGroup(e.target.value)}
            className="w-full p-2 border border-gray-600 rounded-md bg-gray-700 text-white focus:border-blue-400 focus:outline-none"
          >
            <option value="18-25">18 - 25</option>
            <option value="26-40">26 - 40</option>
            <option value="41+">41+</option>
          </select>
        </div>

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

        <button
          onClick={handleSaveAndGo}
          className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-2 rounded-lg font-medium transition"
        >
          {language === "en"
            ? "Save Profile & Go to Chat"
            : "प्रोफ़ाइल सहेजें और चैट पर जाएँ"}
        </button>
      </div>
    </div>
  );
}