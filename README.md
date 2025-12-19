## Prerequisites

- Python 3.11+
- PostgreSQL (or use SQLite for development)
- **Ollama** ([Install here](https://ollama.ai/download))
- Docker & Docker Compose (optional)

## Ollama Setup

### 1. Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai/download

### 2. Pull the Model
```bash
# Start Ollama service
ollama serve

# In another terminal, pull llama3.2 (recommended)
ollama pull llama3.2

# Or use other models:
# ollama pull llama2
# ollama pull mistral
# ollama pull codellama
```

### 3. Verify Ollama is Running
```bash
curl http://localhost:11434/api/tags
```

## Installation

### Local Setup (Without Docker)

1. **Install Ollama and pull model** (see above)

2. **Clone repository**
```bash
git clone https://github.com/yourusername/ai-api-testing-assistant.git
cd ai-api-testing-assistant
```

3. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Set up environment**
```bash
cat > .env << EOF
DATABASE_URL=sqlite:///./test.db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
SECRET_KEY=your-secret-key
EOF
```

6. **Initialize database**
```bash
python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

7. **Make sure Ollama is running**
```bash
ollama serve
```

8. **Run application**
```bash
uvicorn app.main:app --reload
```

9. **Open browser**
Navigate to `http://localhost:8000`

### Docker Setup

**Important:** Docker will automatically pull and run Ollama for you!

1. **Start all services**
```bash
docker-compose up --build
```

2. **Pull the model (first time only)**
```bash
# Wait for containers to start, then:
docker-compose exec ollama ollama pull llama3.2
```

3. **Access application**
Navigate to `http://localhost:8000`

## Configuration

### Choosing a Different Model

In `.env`, you can use any Ollama model:
```bash
# Faster, lighter (recommended for laptops)
OLLAMA_MODEL=llama3.2

# Better quality (requires more RAM)
OLLAMA_MODEL=llama2

# Code-focused
OLLAMA_MODEL=codellama

# Lightweight
OLLAMA_MODEL=mistral
```

### Model Requirements

| Model | RAM Required | Speed | Quality |
|-------|-------------|-------|---------|
| llama3.2 | 8GB | Fast | Good |
| llama2 | 8GB | Medium | Better |
| mistral | 4GB | Very Fast | Good |
| codellama | 8GB | Medium | Best for code |

## Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **Database**: PostgreSQL (SQLite for development)
- **AI**: Ollama (Local LLM - llama3:latest)
- **Testing**: Pytest, Coverage
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Deployment**: Docker, Docker Compose

## Why Ollama?

✅ **Completely Free** - No API costs
✅ **Privacy** - Runs entirely on your machine
✅ **No Rate Limits** - Use as much as you want
✅ **Offline** - Works without internet
✅ **Resume-Worthy** - Shows you can work with local LLMs
✅ **Fast** - Low latency responses
## Example Test Scenarios

### Test Your Own API

1. **Upload this OpenAPI specification**

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "AI Testing Assistant Health API",
    "version": "1.0.0"
  },
  "paths": {
    "/health": {
      "get": {
        "responses": {
          "200": {
            "description": "Health check endpoint",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "status": {
                      "type": "string",
                      "example": "healthy"
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

<img width="1389" height="872" alt="Screenshot 2025-12-19 095815" src="https://github.com/user-attachments/assets/6ed044bf-db30-4e3f-a623-5e376d793232" />


2. **Generate tests** from the uploaded spec.
<img width="1046" height="656" alt="image" src="https://github.com/user-attachments/assets/70a6be0d-4cbd-4f49-9878-0bc9467f87ee" />
<img width="522" height="373" alt="image" src="https://github.com/user-attachments/assets/34fd730d-e0ed-4844-bde6-c414980aa3e7" />

3. **Execute tests with base URL**
```bash
http://localhost:8000
```
<img width="1094" height="608" alt="image" src="https://github.com/user-attachments/assets/a7061049-8013-4cd1-8ac3-d86f42caf66e" />



4. **Expected result**
- All generated tests should pass successfully.
<img width="1365" height="545" alt="image" src="https://github.com/user-attachments/assets/9cd4db7d-e448-4e64-b5a3-ce77fe7edd4b" />
<img width="310" height="810" alt="image" src="https://github.com/user-attachments/assets/4c6a89b7-0a8d-4c89-a6f5-653944ac05e2" />
<img width="1328" height="1110" alt="image" src="https://github.com/user-attachments/assets/8157c5e2-1230-40d9-9dc0-55b16022da16" />


---

### Test Public APIs

- **GitHub API**
```bash
https://api.github.com
```

- **ReqRes.in**
```bash
https://reqres.in
```

- **JSONPlaceholder** (recommended demo)
```bash
https://jsonplaceholder.typicode.com
```

---

## Troubleshooting

### "Ollama connection failed"

```bash
# Check if Ollama is running
ollama ps

# Start Ollama
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

---

### "Invalid JSON format"

- Use the **exact JSON** from the example above
- Validate JSON at:
```bash
https://jsonformatter.curiousconcept.com
```
- Remove trailing commas

---

### "404 errors" in tests

- Ensure the **Base URL** is correct
- Test manually first:

```bash
curl https://jsonplaceholder.typicode.com/posts
```

- The endpoint must exist in the target API

---

### "AI analysis shows empty"

- Wait for tests to complete:
```bash
status = "completed"
```

- Check Ollama is running:
```bash
ollama list
```

- Use the JSONPlaceholder example (always works)

---

### "Critical Issues shows blank"

- Hard refresh browser:
```bash
Windows: Ctrl + F5
Mac: Cmd + Shift + R
```

- Empty lists now show:
```bash
None
```
