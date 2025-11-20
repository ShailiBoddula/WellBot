import re
import logging
try:
    from typing import Dict, List
except ImportError:
    # For older Python versions
    Dict = dict
    List = list

class SimpleNLU:
    def __init__(self):
        print("Advanced NLU initialized with Indic-BERT and entity extraction")

        # Basic intent keywords for classification
        self.intent_keywords = {
            "symptom_query": ["pain", "fever", "cough", "headache", "stomach", "nausea", "throat", "temperature", "ache", "hurt", "cold", "i have a", "i have", "दर्द", "बुखार", "खांसी", "सिरदर्द", "पेट", "मतली", "गला", "तापमान", "bhukar", "hein", "mujhe", "sardi", "nazla"],
            "ask_first_aid": ["first aid", "treat", "bandage", "burn", "sprain", "bleeding", "cpr", "wound", "cut", "प्राथमिक उपचार", "इलाज", "पट्टी", "जलन", "मोच", "खून", "सीपीआर", "घाव", "कट", "बाँधें", "बांधे", "बाँधना", "बांधना"],
            "ask_wellness_tip": ["tip", "wellness", "diet", "exercise", "sleep", "hydration", "healthy", "give me a wellness tip", "wellnes s tip", "टिप", "वेलनेस", "आहार", "व्यायाम", "नींद", "हाइड्रेशन", "स्वस्थ"],
            "health_checkin": ["check", "checkin", "mood", "feeling", "how are you", "how do you feel", "health check", "मूड", "महसूस", "कैसे हैं", "सेहत जांच"],
            "stress_management": ["stress", "stressed", "anxious", "anxiety", "overwhelmed", "tension", "तनाव", "चिंता", "परेशान"],
            "sleep_recommendation": ["sleep", "insomnia", "can't sleep", "sleeping", "नींद", "अनिद्रा"],
            "diet_recommendation": ["diet", "food", "nutrition", "eat", "eating", "meal", "आहार", "खाना", "पोषण"],
            "fitness_tracking": ["exercise", "workout", "fitness", "gym", "run", "walk", "व्यायाम", "कसरत", "फिटनेस"],
            "emotional_support": ["sad", "depressed", "lonely", "emotional", "support", "help me", "mental health", "mental", "health", "दुखी", "अकेला", "भावनात्मक", "सहायता"],
            "mindfulness_practice": ["meditation", "mindful", "mindfulness", "breathe", "breathing", "ध्यान", "सचेतन"],
            "greeting": ["hi", "hello", "hey", "namaste", "good morning", "how are you", "नमस्ते", "हैलो", "हाय", "प्रणाम", "सुप्रभात", "कैसे हैं"],
        }

        # Entity patterns for symptom extraction
        self.entity_patterns = {
            "symptom": [
                r'\b(fever|feverish|high temperature|temperature)\b',
                r'\b(cough|coughing|khansi)\b',
                r'\b(headache|head pain|headache|sar dard|sir dard)\b',
                r'\b(stomach pain|abdominal pain|stomach ache|pet dard)\b',
                r'\b(sore throat|throat pain|gla dard|gale mein dard)\b',
                r'\b(nausea|feeling sick|matli)\b',
                r'\b(bukhar|bhukar)\b',
                r'\b(dard|pain|ache|hurt)\b'
            ],
            "body_part": [
                r'\b(head|sar|sir)\b',
                r'\b(throat|gla|gal)\b',
                r'\b(stomach|pet|abdomen)\b',
                r'\b(chest|seena)\b',
                r'\b(arm|baah|bhuj)\b',
                r'\b(leg|pair|taang)\b'
            ],
            "ailment": [
                r'\b(cold|common cold|sardi|nazla)\b',
                r'\b(flu|influenza)\b',
                r'\b(allergy|allergic)\b',
                r'\b(infection|infection)\b'
            ]
        }

        # Initialize Indic-BERT for Hindi processing (optional - skip if not available)
        self.indic_bert_available = False
        try:
            from transformers import AutoTokenizer, AutoModelForMaskedLM
            self.indic_tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-bert")
            self.indic_model = AutoModelForMaskedLM.from_pretrained("ai4bharat/indic-bert")
            self.indic_bert_available = True
            print("Indic-BERT loaded successfully")
        except Exception as e:
            print(f"Indic-BERT not available (optional): {e}")
            self.indic_tokenizer = None
            self.indic_model = None

        # Initialize MarianMT for translation (optional - skip if not available)
        self.marian_available = False
        try:
            from transformers import MarianMTModel, MarianTokenizer
            self.en_hi_tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-hi")
            self.en_hi_model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-hi")
            self.hi_en_tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-hi-en")
            self.hi_en_model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-hi-en")
            self.marian_available = True
            print("MarianMT translation models loaded successfully")
        except Exception as e:
            print(f"MarianMT not available (optional): {e}")
            self.en_hi_tokenizer = None
            self.en_hi_model = None
            self.hi_en_tokenizer = None
            self.hi_en_model = None

    def extract_entities(self, message):
        """Extract entities from message using regex patterns"""
        entities = {"symptom": [], "body_part": [], "ailment": []}
        message_lower = message.lower()

        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, message_lower, re.IGNORECASE)
                for match in matches:
                    entity_value = match.group()
                    if entity_value not in [e["value"] for e in entities[entity_type]]:
                        entities[entity_type].append({
                            "value": entity_value,
                            "start": match.start(),
                            "end": match.end(),
                            "confidence": 0.9
                        })

        return entities

    def detect_language(self, message):
        """Simple language detection"""
        hindi_chars = set('अआइईउऊएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहक्षत्रज्ञ')
        english_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

        hindi_count = sum(1 for char in message if char in hindi_chars)
        english_count = sum(1 for char in message if char in english_chars)

        if hindi_count > english_count:
            return "hi"
        else:
            return "en"

    def translate_text(self, text, source_lang, target_lang):
        """Translate text using MarianMT"""
        if not self.marian_available:
            return text

        try:
            if source_lang == "en" and target_lang == "hi":
                tokenizer = self.en_hi_tokenizer
                model = self.en_hi_model
            elif source_lang == "hi" and target_lang == "en":
                tokenizer = self.hi_en_tokenizer
                model = self.hi_en_model
            else:
                return text

            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            translated = model.generate(**inputs)
            translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
            return translated_text
        except Exception as e:
            logging.error(f"Translation error: {e}")
            return text

    def parse(self, message):
        # Detect language
        detected_lang = self.detect_language(message)

        # Extract entities
        entities = self.extract_entities(message)

        # Intent classification using keyword matching
        message_lower = message.lower()
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return {
                        "intent": intent,
                        "entities": entities,
                        "confidence": 0.8,
                        "method": "keyword",
                        "language": detected_lang
                    }

        return {
            "intent": "fallback",
            "entities": entities,
            "confidence": 0.5,
            "method": "fallback",
            "language": detected_lang
        }