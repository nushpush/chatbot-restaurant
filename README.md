# Restaurant Chatbot

A full-stack chatbot application for restaurant services with AI-powered conversational capabilities.

## Features

- **AI-Powered Chat**: Intelligent chatbot using RAG (Retrieval-Augmented Generation) and recipe agents
- **Real-time Communication**: WebSocket-based chat service
- **User Authentication**: Secure login and user management
- **Chat History**: Persistent conversation storage and retrieval
- **Food Guardrails**: Content filtering and safety measures
- **GraphRAG Integration**: Advanced knowledge graph retrieval
- **Embeddings Generation**: Vector-based semantic search

## Tech Stack

### Backend (Python)
- FastAPI/Flask for API services
- LangChain for LLM orchestration
- Redis for caching
- LanceDB for vector storage
- PostgreSQL/SQLite for data persistence

### Frontend (React)
- React.js
- WebSocket for real-time chat
- Modern UI components

## Project Structure

```
chatbot-restaurant/
├── Chatbot_Backend_Python/
│   ├── agents/           # AI agents (RAG, recipe, chat memory)
│   ├── dbmodel/          # Database models
│   ├── services/         # API and authentication services
│   ├── guardrail/        # Content filtering and safety
│   ├── graphrag/         # Graph-based retrieval
│   ├── retriever/        # Information retrieval
│   └── utils/            # Utility functions
└── Chatbot_Frontend/
    └── src/
        └── services/     # Frontend services and components
```

## Setup

### Backend Setup

1. Install dependencies:
```bash
cd Chatbot_Backend_Python
pip install -r requirements.txt
```

2. Configure environment variables (create `.env` file)

3. Run the backend server:
```bash
python app.py
```

### Frontend Setup

1. Install dependencies:
```bash
cd Chatbot_Frontend
npm install
```

2. Start the development server:
```bash
npm start
```

## Testing

Run tests for backend:
```bash
cd Chatbot_Backend_Python
pytest
```

Run tests for frontend:
```bash
cd Chatbot_Frontend
npm test
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]