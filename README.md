# WellBot

A multilingual wellness chatbot built with React frontend and Flask backend, providing health information and support in English and Hindi.

## Features

- **Multilingual Support**: Conversations in English and Hindi
- **Knowledge Base**: Comprehensive health information with symptoms, self-care, and when to seek doctor advice
- **User Authentication**: Secure login with JWT tokens
- **Chat Interface**: Interactive chat with the bot
- **Feedback System**: Users can provide feedback on responses
- **Admin Dashboard**: Analytics, user stats, and knowledge base management
- **Profile Management**: User profiles and personal statistics

## Tech Stack

### Frontend
- React 18
- Vite
- Tailwind CSS
- React Router DOM
- Axios
- Recharts

### Backend
- Flask
- Rasa (NLU)
- OpenAI API
- SQLite
- Transformers (Hugging Face)
- Indic NLP Library

## Installation

### Prerequisites
- Node.js (for frontend)
- Python 3.8+ (for backend)
- OpenAI API key

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key: `OPENAI_API_KEY=your_key_here`

4. Initialize the database:
   ```bash
   python db_setup.py
   ```

5. Run the backend server:
   ```bash
   python app.py
   ```
   The server will start on `http://localhost:8000`

### Frontend Setup
1. Install Node.js dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173`

## Usage

1. Open the frontend in your browser
2. Register/Login with your email
3. Start chatting with WellBot in English or Hindi
4. Access admin features via the Dashboard (admin role required)
5. View your profile and statistics

## API Endpoints

- `POST /auth/login` - User authentication
- `POST /chat` - Send chat messages
- `POST /feedback` - Submit feedback
- `GET /admin/stats` - Admin statistics
- `GET/POST/PUT/DELETE /admin/kb` - Knowledge base management
- `GET /profile` - User profile
- `GET /user/stats` - User statistics

## Disclaimer

WellBot provides general health information and is not a substitute for professional medical advice. Always consult healthcare professionals for personalized guidance.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
