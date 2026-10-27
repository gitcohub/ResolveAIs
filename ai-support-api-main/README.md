# ResolveAI API

A production-minded FastAPI demo for validating, classifying, and processing customer support requests.

The project demonstrates practical backend patterns for AI-powered applications:

- Clean REST API endpoints
- Pydantic request and response validation
- Async request handling
- Optional OpenAI integration
- Mock fallback without API credentials
- Background job submission and status polling
- Structured provider error handling
- Automatic OpenAPI / Swagger documentation
- Automated API tests
- Dockerized local deployment

## Use Case

A customer support application can submit a customer message and receive:

- A support category
- A priority level
- A suggested customer-facing reply
- The processing mode used (`mock` or `openai`)

Long-running requests can also be submitted as background jobs.

## Architecture

```text
Client
  |
  v
FastAPI endpoints
  |
  +--> Pydantic validation
  |
  +--> Support classification
  |
  +--> OpenAI service or mock fallback
  |
  +--> Structured API response
```

Background workflow:

```text
POST /support/jobs
        |
        v
202 Accepted + job_id
        |
        v
Background processing
        |
        v
GET /support/jobs/{job_id}
        |
        v
completed / failed result
```

## API Endpoints

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "ai_mode": "mock"
}
```

### Analyze a Support Request

```http
POST /support/analyze
```

Example request:

```json
{
  "message": "My order has not arrived and I need an update.",
  "priority": "high"
}
```

Example response:

```json
{
  "category": "shipping",
  "priority": "high",
  "suggested_reply": "Thank you for contacting our support team. We have received your request and will review it shortly.",
  "processing_mode": "mock"
}
```

### Submit a Background Job

```http
POST /support/jobs
```

The endpoint returns `202 Accepted` with a job identifier:

```json
{
  "job_id": "example-job-id",
  "status": "queued",
  "status_url": "/support/jobs/example-job-id"
}
```

### Check Job Status

```http
GET /support/jobs/{job_id}
```

Example completed response:

```json
{
  "job_id": "example-job-id",
  "status": "completed",
  "result": {
    "category": "shipping",
    "priority": "high",
    "suggested_reply": "Thank you for contacting our support team. We have received your request and will review it shortly.",
    "processing_mode": "mock"
  },
  "error": null
}
```

## Local Setup

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

The application works in mock mode when no API key is provided:

```env
OPENAI_API_KEY=
OPENAI_MODEL=your-available-model-name
```

### 4. Start the API

```powershell
uvicorn app.main:app --reload --port 8010
```

Open:

- API documentation: `http://127.0.0.1:8010/docs`
- Health endpoint: `http://127.0.0.1:8010/health`

## Tests

Run the complete test suite:

```powershell
pytest -v
```

The tests cover:

- Health endpoint behavior
- Valid support request processing
- Pydantic validation failures
- Background job processing
- Unknown job handling

## Docker

Build the image:

```powershell
docker build -t ai-support-api .
```

Run it with an isolated host port:

```powershell
docker run --rm --name ai-support-api-demo -p 18010:8010 ai-support-api
```

Open:

- `http://127.0.0.1:18010/docs`
- `http://127.0.0.1:18010/health`

## Design Decisions

### Async API Calls

External AI requests are network-bound operations, so the provider integration uses an asynchronous client rather than blocking the server thread.

### Mock Fallback

The application remains fully testable without paid API credentials. This makes local development and automated testing predictable and inexpensive.

### Background Processing

FastAPI `BackgroundTasks` and an in-memory job store are used to demonstrate the request pattern clearly.

For a production deployment, the in-memory implementation should be replaced with durable infrastructure such as Redis, a task queue, or a managed cloud queue.

### Input Validation

Pydantic models enforce message length, allowed priority values, and consistent response structures. Invalid input receives a standard `422` response.

### Provider Error Handling

Timeouts, connection failures, and upstream API errors are converted into clear HTTP responses instead of exposing raw exceptions.

## Current Limitations

- Background job state is stored in memory and is lost when the application restarts.
- The mock classifier uses simple keyword matching.
- Authentication and rate limiting are not yet implemented.
- No persistent database is currently used.
- Real AI responses require valid provider credentials and API billing.

## Production Improvements

Potential next steps include:

- Redis-backed job storage
- Celery, RQ, or a managed cloud queue
- Authentication and rate limiting
- Persistent conversation history
- Structured model outputs
- Logging and observability
- Database integration
- CI/CD deployment
- Retrieval-augmented support answers

## Project Status

The current version includes:

- Working FastAPI endpoints
- Pydantic validation
- Async request handling
- Mock and optional AI processing modes
- Background job submission and polling
- Automated tests
- Docker support
- Swagger documentation