# Sparky Backend

A backend service for a Walmart-like shopping assistant, built with FastAPI and OpenAI Agents. This project provides intelligent product search, cart management, and user interaction capabilities using advanced AI models and a vector database.

## Features

- **AI Shopping Assistant**: Uses OpenAI GPT-4.1 to help users search, recommend, and manage products.
- **Cart Management**: Add, remove, and view items in the user's cart with JWT-based authentication.
- **Product Search**: Supports search by category, product ID, and fuzzy queries.
- **Vector Store Retrieval**: Retrieves relevant products using vector embeddings and MongoDB.
- **Structured Responses**: Optionally structures product responses with product IDs in XML tags.
- **Logging**: In-memory and file-based logging for API requests and errors.
- **Docker Support**: Easily build and run the backend in a containerized environment.

## Project Structure

```
main.py           # FastAPI application entrypoint
wrapper.py        # Main agent orchestration and response handling
cartAgent.py      # Cart management agent and tools
cartTools.py      # Cart-related API tool functions
ragAgent.py       # Vector store retrieval agent
searchTools.py    # Product search tool functions
utils.py          # Shared utilities and user model
test.py           # Example/test agent usage
Dockerfile        # Docker build instructions
pyproject.toml    # Python dependencies and project metadata
fastapi.logs      # Log file (runtime generated)
```

## Setup

- Recommendation: Use uv instead of pip. (uv is an extremely fast Python package and project manager, written in Rust). checkout more details [uv](https://docs.astral.sh/uv/)

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (for dependency management)
- Docker (optional, for containerized deployment)
- MongoDB instance (for product vector search)
- OpenAI API key and organization/project (for GPT-4.1 and embeddings)

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/timetooth/sparky.git
   cd sparky_backend
   ```
2. **Install dependencies:**
   ```sh
   uv sync
   ```
3. **Set environment variables:**
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `OPENAI_ORG_KEY`: Your OpenAI organization key
   - `OPENAI_PROJECT_ID`: Your OpenAI project ID
   - `NODE_BASE_URI`: Base URI for the Node.js backend
   - `MONGO_URI`: MongoDB connection string
   - (Optional) `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins or * for dev environment, example ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5500

   You can use a .env file in the project root:
   ```
   OPENAI_API_KEY=sk-...
   OPENAI_ORG_KEY=...
   OPENAI_PROJECT_ID=...
   NODE_BASE_URI=
   MONGO_URI=
   ALLOWED_ORIGINS=
   ```

4. **Run the server:**
   ```sh
   .venv/bin/fastapi run main.py
   ```
   Or use Docker:
   ```sh
   docker build -t sparky .
   docker run -p 8000:10000 sparky
   ```
   Or use uv: (recommended for development)
   ```sh
   uv run fastapi dev
   ```

## API Endpoints

- `GET /` — Health check
- `POST /agent_response` — Get AI agent response (see below for payload)
- `GET /logs` — Get recent logs
- `GET /logs/download` — Download log file
- `DELETE /logs/delete` — Clear logs
- `GET /cors` — Get allowed CORS origins

### Example: `/agent_response` Payload

```json
{
  "user_name": "Alice",
  "user_age": 28,
  "user_input": "Add 2 red t-shirts to my cart",
  "user_jwt": "<JWT_TOKEN>",
  "last_response_id": null,
  "use_structuring": true
}
```

### Response

```json
{
  "new_message_id": "...",
  "user_input": "Add 2 red t-shirts to my cart",
  "final_output": "...response..."
}
```

## Agents & Tools

- **Cart Manager**: Handles cart operations (add, remove, view, clear)
- **Search Tools**: Search by category, ID, or fuzzy query
- **RAG Agent**: Retrieves products using vector search
- **User Info Tool**: Returns user details

## Testing

- Run test.py for agent and tool usage examples.
- Use the `/logs` endpoint to monitor API activity.
