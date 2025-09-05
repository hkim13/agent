# Memory Agent

A LangGraph-based memory agent with user profile and todo management capabilities.

## Features

- **User Profile Management**: Stores and updates user information (name, location, job, connections, interests)
- **Todo List Management**: Creates, updates, and tracks todo items with status and solutions
- **Memory Persistence**: Maintains conversation context and user preferences
- **REST API**: FastAPI-based web service for easy integration

## Railway Deployment

This application is configured for deployment on Railway.

### Required Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `USER_ID`: User identifier (optional, defaults to "default-user")
- `PORT`: Server port (Railway sets this automatically)

### API Endpoints

- `GET /`: Health check
- `GET /health`: Service health status
- `POST /chat`: Main chat endpoint
- `GET /memory/{user_id}`: Retrieve stored memories for a user

### Chat API Usage

```bash
curl -X POST "https://your-app.railway.app/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello! My name is John and I live in New York."}
    ],
    "user_id": "user123"
  }'
```

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```

3. Run the application:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`
