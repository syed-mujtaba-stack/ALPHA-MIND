# ALPHA MIND – Intelligent Hybrid AI Chatbot System

A powerful hybrid AI chat platform that combines cloud AI models (via OpenRouter) with local/offline models (via liteLLM) for fast, cheap, and privacy-focused AI conversations.

## 🚀 Features

### Core Features
- **Hybrid AI System**: Switch between cloud (OpenRouter) and local (liteLLM) models
- **Multiple AI Models**: GPT-4, Claude 3.5, Gemini, Llama, Grok, Deepseek, and local models
- **Streaming Chat**: Real-time responses like ChatGPT
- **Smart Routing**: Automatic fallback between cloud and local models
- **File Analysis**: PDF, Image, Excel upload and analysis
- **Code Assistant**: Bug fixing, code generation, project structure builder
- **User System**: Firebase Authentication with profiles and history
- **Dark/Light Mode**: Modern UI with theme switching

### Advanced Features
- Voice Chat (Speech → Text)
- Text → Speech (AI voice)
- Image Generation
- Document Summaries
- Web Search Mode
- AI Agents (Task automation)

## 🏗️ Architecture

```
┌────────────────────────────┐
│     React.js Frontend       │
│  (TypeScript + Tailwind)    │
└───────────────┬────────────┘
                │
                ▼
┌────────────────────────────┐
│ Firebase Authentication     │
│ Frontend Login + ID Token   │
└───────────────┬────────────┘
                │ Bearer Token
                ▼
┌────────────────────────────┐
│      Django Backend         │
│  - Token Verification       │
│  - Route to AI Engine       │
└───────────────┬────────────┘
                │
┌────────────────┴────────────────┐
▼                                 ▼
┌────────────────────────┐        ┌────────────────────────────┐
│ OpenRouter API         │        │ liteLLM Local Gateway       │
│ Cloud Models           │        │ GPU/CPU Local Models        │
└────────────────────────┘        └────────────────────────────┘
```

## 📁 Project Structure

```
ALPHA MIND/
│
├── frontend/           # React.js + TypeScript + Tailwind
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── utils/
│   │   └── types/
│   ├── public/
│   └── package.json
│
├── backend/            # Django REST Framework
│   ├── chat/
│   ├── users/
│   ├── models/
│   ├── auth/
│   ├── utils/
│   └── requirements.txt
│
├── local-llm/          # liteLLM Configuration
│   ├── liteLLM.yaml
│   ├── models/
│   └── scripts/
│
├── docs/              # Documentation
│   ├── api.md
│   ├── deployment.md
│   └── setup.md
│
└── README.md
```

## 🛠️ Tech Stack

### Frontend
- **React.js** with TypeScript
- **Tailwind CSS** for styling
- **Firebase** for authentication
- **Axios** for API calls
- **React Router** for navigation

### Backend
- **Django** with REST Framework
- **Firebase Admin SDK** for token verification
- **OpenRouter API** for cloud models
- **liteLLM** for local models
- **Redis** for caching (optional)

### AI Models
- **Cloud Models**: GPT-4, Claude 3.5, Gemini, Llama, Grok, Deepseek
- **Local Models**: Llama 3.2, Phi-3, Mistral (via liteLLM)

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- Django 4.0+
- Firebase Project
- OpenRouter API Key
- GPU (for local models, optional)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ALPHA-MIND
```

2. **Frontend Setup**
```bash
cd frontend
npm install
cp .env.example .env.local
# Add Firebase config to .env.local
npm start
```

3. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add API keys to .env
python manage.py migrate
python manage.py runserver
```

4. **Local Models Setup (Optional)**
```bash
cd local-llm
pip install litellm
# Configure liteLLM.yaml
# Download local models
```

## 🔧 Configuration

### Environment Variables

**Frontend (.env.local)**
```
REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
REACT_APP_FIREBASE_APP_ID=your_app_id
REACT_APP_API_URL=http://localhost:8000
```

**Backend (.env)**
```
SECRET_KEY=your_django_secret_key
DEBUG=True
FIREBASE_PROJECT_ID=your_project_id
OPENROUTER_API_KEY=your_openrouter_key
LITELLM_HOST=http://localhost:4000
DATABASE_URL=sqlite:///db.sqlite3
```

## 📖 API Documentation

### Authentication
- `POST /api/auth/check/` - Verify Firebase token

### Chat
- `POST /api/chat/stream/` - Stream AI responses
- `GET /api/chat/history/` - Get chat history
- `POST /api/chat/save/` - Save conversation

### Models
- `GET /api/models/list/` - List available models
- `POST /api/models/switch/` - Switch active model

### Files
- `POST /api/files/upload/` - Upload file for analysis
- `POST /api/files/analyze/` - Analyze uploaded file

## 🎯 Usage

1. **Sign up/login** with Firebase Authentication
2. **Choose your AI model** from the dropdown
3. **Start chatting** with streaming responses
4. **Upload files** for analysis (PDF, images, Excel)
5. **Switch to code mode** for development assistance
6. **Enable offline mode** for local model usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenRouter for providing unified AI model access
- liteLLM for local model integration
- Firebase for authentication services
- Django Team for the excellent framework

---

Built with ❤️ by the ALPHA MIND team
