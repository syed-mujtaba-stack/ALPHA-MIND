<<<<<<< HEAD
# 🚀 ALPHA MIND - Intelligent Hybrid AI Chatbot System

A powerful hybrid AI chat platform that combines cloud AI models (via OpenRouter) with local/offline models (via liteLLM) for fast, cheap, and privacy-focused AI conversations.

## ✨ Features

### Core Features
- 🔄 **Hybrid AI System**: Switch between cloud (OpenRouter) and local (liteLLM) models
- 🤖 **Multiple AI Models**: GPT-4, Claude 3.5, Gemini, Llama, Grok, Deepseek, and local models
- ⚡ **Streaming Chat**: Real-time responses like ChatGPT
- 🧠 **Smart Routing**: Automatic fallback between cloud and local models
- 📁 **File Analysis**: PDF, Image, Excel upload and analysis
- 💻 **Code Assistant**: Bug fixing, code generation, project structure builder
- 👤 **User System**: Firebase Authentication with profiles and history
- 🌙 **Dark/Light Mode**: Modern UI with theme switching

### Advanced Features
- 🎤 **Voice Chat**: Speech → Text & Text → Speech
- 🎨 **Image Generation**: AI-powered image creation
- 📄 **Document Summaries**: Smart document analysis
- 🔍 **Web Search Mode**: Real-time web information
- 🤖 **AI Agents**: Task automation
=======
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
>>>>>>> a292e4ad0da2c086dba7743d30e0b3f830e7b183

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
<<<<<<< HEAD
│   ├── alpha_mind/      # Django project settings
│   ├── chat/            # Chat functionality
│   ├── users/           # User management
│   ├── files/           # File upload & analysis
│   ├── gateway/         # AI model gateway
│   └── requirements.txt
│
├── ai_engine/           # FastAPI AI Engine
│   ├── main.py          # FastAPI app
│   ├── models.py        # Pydantic models
│   ├── services.py      # AI services
│   ├── providers.py     # AI providers
│   └── requirements.txt
=======
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
>>>>>>> a292e4ad0da2c086dba7743d30e0b3f830e7b183
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
<<<<<<< HEAD
- **Zustand** for state management
- **React Query** for data fetching
=======
>>>>>>> a292e4ad0da2c086dba7743d30e0b3f830e7b183

### Backend
- **Django** with REST Framework
- **Firebase Admin SDK** for token verification
- **OpenRouter API** for cloud models
- **liteLLM** for local models
- **Redis** for caching (optional)

<<<<<<< HEAD
### AI Engine
- **FastAPI** for AI model gateway
- **OpenAI** for API compatibility
- **litellm** for local model integration
- **transformers** for local models
=======
### AI Models
- **Cloud Models**: GPT-4, Claude 3.5, Gemini, Llama, Grok, Deepseek
- **Local Models**: Llama 3.2, Phi-3, Mistral (via liteLLM)
>>>>>>> a292e4ad0da2c086dba7743d30e0b3f830e7b183

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- Django 4.0+
- Firebase Project
- OpenRouter API Key
- GPU (for local models, optional)

### Installation

<<<<<<< HEAD
#### 1. Clone the repository
=======
1. **Clone the repository**
>>>>>>> a292e4ad0da2c086dba7743d30e0b3f830e7b183
```bash
git clone <repository-url>
cd ALPHA-MIND
```

<<<<<<< HEAD
#### 2. Frontend Setup
=======
2. **Frontend Setup**
>>>>>>> a292e4ad0da2c086dba7743d30e0b3f830e7b183
```bash
cd frontend
npm install
cp .env.example .env.local
# Add Firebase config to .env.local
npm start
```

<<<<<<< HEAD
#### 3. Backend Setup
=======
3. **Backend Setup**
>>>>>>> a292e4ad0da2c086dba7743d30e0b3f830e7b183
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

<<<<<<< HEAD
#### 4. AI Engine Setup
```bash
cd ai_engine
pip install -r requirements.txt
cp .env.example .env
# Configure OpenRouter API key
uvicorn main:app --reload
```

#### 5. Local Models Setup (Optional)
```bash
cd ai_engine
=======
4. **Local Models Setup (Optional)**
```bash
cd local-llm
>>>>>>> a292e4ad0da2c086dba7743d30e0b3f830e7b183
pip install litellm
# Configure liteLLM.yaml
# Download local models
```

## 🔧 Configuration

### Environment Variables

<<<<<<< HEAD
#### Frontend (.env.local)
```env
=======
**Frontend (.env.local)**
```
>>>>>>> a292e4ad0da2c086dba7743d30e0b3f830e7b183
REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
REACT_APP_FIREBASE_APP_ID=your_app_id
REACT_APP_API_URL=http://localhost:8000
<<<<<<< HEAD
REACT_APP_AI_ENGINE_URL=http://localhost:4000
```

#### Backend (.env)
```env
=======
```

**Backend (.env)**
```
>>>>>>> a292e4ad0da2c086dba7743d30e0b3f830e7b183
SECRET_KEY=your_django_secret_key
DEBUG=True
FIREBASE_PROJECT_ID=your_project_id
OPENROUTER_API_KEY=your_openrouter_key
LITELLM_HOST=http://localhost:4000
DATABASE_URL=sqlite:///db.sqlite3
```

<<<<<<< HEAD
#### AI Engine (.env)
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
LITELLM_HOST=http://localhost:4000
LITELLM_API_KEY=your_litellm_api_key_here
LOCAL_MODEL_PATH=./models
GPU_ENABLED=true
```

=======
>>>>>>> a292e4ad0da2c086dba7743d30e0b3f830e7b183
## 📖 API Documentation

### Authentication
- `POST /api/auth/check/` - Verify Firebase token

### Chat
<<<<<<< HEAD
- `POST /api/chat/send/` - Send chat message
- `GET /api/chat/history/<session_id>/` - Get chat history
- `POST /api/chat/save/` - Save conversation
- `GET /api/chat/sessions/` - List chat sessions
=======
- `POST /api/chat/stream/` - Stream AI responses
- `GET /api/chat/history/` - Get chat history
- `POST /api/chat/save/` - Save conversation
>>>>>>> a292e4ad0da2c086dba7743d30e0b3f830e7b183

### Models
- `GET /api/models/list/` - List available models
- `POST /api/models/switch/` - Switch active model

### Files
- `POST /api/files/upload/` - Upload file for analysis
- `POST /api/files/analyze/` - Analyze uploaded file
<<<<<<< HEAD
- `GET /api/files/list/` - List uploaded files
=======
>>>>>>> a292e4ad0da2c086dba7743d30e0b3f830e7b183

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

<<<<<<< HEAD
- **OpenRouter** for providing unified AI model access
- **liteLLM** for local model integration
- **Firebase** for authentication services
- **Django Team** for the excellent framework
- **FastAPI** for modern API development

## 📊 Development Status

### ✅ Completed (Phase 1)
- [x] Project structure setup
- [x] Tailwind CSS configuration
- [x] Django backend with all apps
- [x] FastAPI AI Engine
- [x] Database models and migrations
- [x] Environment configuration

### 🚧 In Progress (Phase 2)
- [ ] Firebase Authentication integration
- [ ] Basic chat interface
- [ ] Real-time messaging

### 📋 Planned (Phase 3-5)
- [ ] AI Model Integration
- [ ] Advanced Features
- [ ] Deployment & Testing

---

**Ready to start building the future of AI chatbots? 🚀**
=======
- OpenRouter for providing unified AI model access
- liteLLM for local model integration
- Firebase for authentication services
- Django Team for the excellent framework

---

Built with ❤️ by the ALPHA MIND team
>>>>>>> a292e4ad0da2c086dba7743d30e0b3f830e7b183
