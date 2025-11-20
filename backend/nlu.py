import re

class SimpleNLU:
    def __init__(self):
        self.intent_keywords = {
            "symptom_query": ["pain", "fever", "cough", "headache", "stomach", "nausea", "throat", "temperature", "ache", "hurt", "दर्द", "बुखार", "खांसी", "सिरदर्द", "पेट", "मतली", "गला", "तापमान", "bhukar", "hein", "mujhe"],
            "ask_first_aid": ["first aid", "treat", "bandage", "burn", "sprain", "bleeding", "cpr", "wound", "cut", "प्राथमिक उपचार", "इलाज", "पट्टी", "जलन", "मोच", "खून", "सीपीआर", "घाव", "कट"],
            "ask_wellness_tip": ["tip", "wellness", "diet", "exercise", "sleep", "hydration", "healthy", "टिप", "वेलनेस", "आहार", "व्यायाम", "नींद", "हाइड्रेशन", "स्वस्थ"],
            "health_checkin": ["check", "checkin", "mood", "feeling", "how are you", "how do you feel", "health check", "मूड", "महसूस", "कैसे हैं", "सेहत जांच"],
            "stress_management": ["stress", "stressed", "anxious", "anxiety", "overwhelmed", "tension", "तनाव", "चिंता", "परेशान"],
            "sleep_recommendation": ["sleep", "insomnia", "can't sleep", "sleeping", "नींद", "अनिद्रा"],
            "diet_recommendation": ["diet", "food", "nutrition", "eat", "eating", "meal", "आहार", "खाना", "पोषण"],
            "fitness_tracking": ["exercise", "workout", "fitness", "gym", "run", "walk", "व्यायाम", "कसरत", "फिटनेस"],
            "emotional_support": ["sad", "depressed", "lonely", "emotional", "support", "help me", "दुखी", "अकेला", "भावनात्मक", "सहायता"],
            "mindfulness_practice": ["meditation", "mindful", "mindfulness", "breathe", "breathing", "ध्यान", "सचेतन"],
            "greeting": ["hi", "hello", "hey", "namaste", "good morning", "how are you", "नमस्ते", "हैलो", "गुड मॉर्निंग", "कैसे हैं"],
        }

    def detect_language(self, text):
        # Check for Devanagari characters
        if re.search(r'[\u0900-\u097F]', text):
            return "hi"
        return "en"

    def parse(self, message):
        message_lower = message.lower()
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return {
                        "intent": intent,
                        "entities": {},
                        "confidence": 0.9
                    }
        return {
            "intent": "fallback",
            "entities": {},
            "confidence": 0.5
        }