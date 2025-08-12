# FreelanceX.AI API Reference 📚

> **Complete API Documentation for Enhanced AI-Powered Freelance Assistant**

## 🎯 Overview

This document provides comprehensive API reference for FreelanceX.AI, including all endpoints, data models, authentication, and usage examples.

## 🔐 Authentication

### JWT Token Authentication
All API endpoints require JWT token authentication in the Authorization header:

```bash
Authorization: Bearer <your-jwt-token>
```

### Getting a Token
```bash
POST /auth/login
Content-Type: application/json

{
  "username": "your-email@example.com",
  "password": "your-password"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_at": 1640995200
}
```

## 🤖 Agent API Endpoints

### Route Request
Route a user request to the appropriate agent system.

```http
POST /api/route-request
```

**Request Body:**
```json
{
  "message": "Find Python development jobs with $50-100/hour rates",
  "session_id": "unique-session-id",
  "user_id": "user-123",
  "trace_metadata": {
    "request_id": "req-123",
    "source": "web"
  }
}
```

**Response:**
```json
{
  "success": true,
  "response": "I found 5 Python development opportunities...",
  "routing_decision": {
    "target_agent": "job_search_agent",
    "confidence": 0.95,
    "reasoning": "Request matches job search patterns",
    "handoff_type": "direct",
    "priority": 8,
    "estimated_time": 15.0
  },
  "handoffs": ["job_search_agent"],
  "execution_time": 12.5,
  "trace_id": "trace-abc123",
  "metadata": {
    "agent_used": "job_search_agent",
    "provider": "openai",
    "model": "gpt-4o-mini"
  }
}
```

### Get Agent Status
Get the current status of all agents in the system.

```http
GET /api/agent-status
```

**Response:**
```json
{
  "registered_agents": {
    "executive_agent": "active",
    "cognitive_agent": "active",
    "job_search_agent": "active",
    "proposal_writer_agent": "active",
    "math_agent": "active",
    "web_research_agent": "active",
    "marketing_agent": "active",
    "security_agent": "active",
    "ux_agent": "active",
    "expansion_agent": "active"
  },
  "api_providers": "available",
  "total_agents": 10,
  "triage_agent": "active"
}
```

### Get Memory
Retrieve session memory and context.

```http
GET /api/memory/{session_id}
```

**Response:**
```json
{
  "session_id": "session-123",
  "user_id": "user-123",
  "conversation_history": [
    {
      "role": "user",
      "content": "Find Python development jobs",
      "timestamp": "2024-01-01T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "I found 5 opportunities...",
      "timestamp": "2024-01-01T10:00:05Z",
      "agent": "job_search_agent"
    }
  ],
  "context": {
    "user_preferences": {
      "skills": ["Python", "Django", "React"],
      "rate_range": [50, 100],
      "location": "remote"
    },
    "session_analytics": {
      "total_requests": 5,
      "successful_handoffs": 5,
      "average_response_time": 3.2
    }
  }
}
```

## 🔌 System Management Endpoints

### Health Check
Check the overall health of the system.

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T10:00:00Z",
  "version": "2.0.0",
  "components": {
    "agents": "healthy",
    "database": "healthy",
    "api_providers": "healthy",
    "memory": "healthy"
  },
  "uptime": 3600,
  "memory_usage": "45%",
  "cpu_usage": "12%"
}
```

### Get API Providers
Get status of all configured API providers.

```http
GET /api/providers
```

**Response:**
```json
{
  "providers": {
    "openai": {
      "name": "OpenAI",
      "available": true,
      "model": "gpt-4o-mini",
      "priority": 1,
      "enabled": true,
      "last_used": "2024-01-01T10:00:00Z"
    },
    "gemini": {
      "name": "Google Gemini",
      "available": true,
      "model": "gemini-pro",
      "priority": 2,
      "enabled": true,
      "last_used": "2024-01-01T09:55:00Z"
    }
  },
  "fallback_enabled": true,
  "total_providers": 2,
  "available_providers": 2
}
```

### Test Provider
Test a specific API provider.

```http
POST /api/providers/test
```

**Request Body:**
```json
{
  "provider": "openai"
}
```

**Response:**
```json
{
  "success": true,
  "provider": "openai",
  "response_time": 1.2,
  "model": "gpt-4o-mini",
  "message": "Provider is working correctly"
}
```

## 📊 Analytics Endpoints

### Get Session Analytics
Get analytics for a specific session.

```http
GET /api/analytics/session/{session_id}
```

**Response:**
```json
{
  "session_id": "session-123",
  "user_id": "user-123",
  "start_time": "2024-01-01T09:00:00Z",
  "end_time": "2024-01-01T10:00:00Z",
  "total_requests": 10,
  "successful_requests": 10,
  "failed_requests": 0,
  "average_response_time": 3.5,
  "agent_usage": {
    "job_search_agent": 4,
    "proposal_writer_agent": 3,
    "math_agent": 2,
    "cognitive_agent": 1
  },
  "provider_usage": {
    "openai": 8,
    "gemini": 2
  },
  "performance_metrics": {
    "total_tokens_used": 15000,
    "cost_estimate": 0.45,
    "memory_operations": 25
  }
}
```

### Get System Analytics
Get overall system analytics.

```http
GET /api/analytics/system
```

**Response:**
```json
{
  "period": "last_24_hours",
  "total_sessions": 150,
  "total_requests": 1250,
  "success_rate": 98.5,
  "average_response_time": 3.2,
  "peak_concurrent_users": 25,
  "agent_performance": {
    "job_search_agent": {
      "requests": 450,
      "success_rate": 99.1,
      "average_time": 2.8
    },
    "proposal_writer_agent": {
      "requests": 300,
      "success_rate": 98.5,
      "average_time": 4.2
    }
  },
  "provider_performance": {
    "openai": {
      "requests": 1000,
      "success_rate": 99.0,
      "average_time": 2.5
    },
    "gemini": {
      "requests": 250,
      "success_rate": 97.0,
      "average_time": 3.8
    }
  }
}
```

## 🔧 Configuration Endpoints

### Get Configuration
Get current system configuration.

```http
GET /api/config
```

**Response:**
```json
{
  "agents": {
    "default_model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 4000,
    "enable_tracing": true,
    "enable_guardrails": true,
    "session_timeout": 3600
  },
  "api": {
    "enable_fallback": true,
    "timeout_seconds": 30,
    "max_concurrent_requests": 10
  },
  "security": {
    "enable_encryption": true,
    "enable_audit_logging": true,
    "max_requests_per_minute": 60
  },
  "monitoring": {
    "enable_logging": true,
    "log_level": "INFO",
    "enable_metrics": true
  }
}
```

### Update Configuration
Update system configuration.

```http
PUT /api/config
```

**Request Body:**
```json
{
  "agents": {
    "temperature": 0.8,
    "enable_tracing": false
  },
  "api": {
    "timeout_seconds": 45
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Configuration updated successfully",
  "updated_fields": ["agents.temperature", "agents.enable_tracing", "api.timeout_seconds"]
}
```

## 📝 Data Models

### RoutingDecision
```python
class RoutingDecision(BaseModel):
    target_agent: str
    confidence: float
    reasoning: str
    handoff_type: str = "direct"
    priority: int = 5
    estimated_time: float = 30.0
```

### TriageResult
```python
class TriageResult(BaseModel):
    success: bool
    response: str
    routing_decision: Optional[RoutingDecision]
    handoffs: List[str] = []
    execution_time: float
    trace_id: Optional[str]
    metadata: Dict[str, Any] = {}
```

### SessionContext
```python
class SessionContext(BaseModel):
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    conversation_count: int
    user_preferences: Dict[str, Any] = {}
    analytics: Dict[str, Any] = {}
```

## 🚨 Error Handling

### Error Response Format
All error responses follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "message",
      "issue": "Message cannot be empty"
    },
    "timestamp": "2024-01-01T10:00:00Z",
    "request_id": "req-123"
  }
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `AUTHENTICATION_ERROR` | Invalid or missing authentication | 401 |
| `AUTHORIZATION_ERROR` | Insufficient permissions | 403 |
| `VALIDATION_ERROR` | Invalid request parameters | 400 |
| `AGENT_ERROR` | Agent execution failed | 500 |
| `API_PROVIDER_ERROR` | API provider unavailable | 503 |
| `RATE_LIMIT_ERROR` | Too many requests | 429 |
| `SESSION_ERROR` | Session not found or expired | 404 |

## 📚 Usage Examples

### Python Client Example
```python
import requests
import json

class FreelanceXClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def route_request(self, message, session_id, user_id):
        url = f"{self.base_url}/api/route-request"
        data = {
            "message": message,
            "session_id": session_id,
            "user_id": user_id
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
    
    def get_agent_status(self):
        url = f"{self.base_url}/api/agent-status"
        response = requests.get(url, headers=self.headers)
        return response.json()

# Usage
client = FreelanceXClient("http://localhost:8000", "your-token")
result = client.route_request(
    "Find Python development jobs",
    "session-123",
    "user-123"
)
print(result)
```

### cURL Examples
```bash
# Route a request
curl -X POST "http://localhost:8000/api/route-request" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find Python development jobs",
    "session_id": "session-123",
    "user_id": "user-123"
  }'

# Get agent status
curl -X GET "http://localhost:8000/api/agent-status" \
  -H "Authorization: Bearer your-token"

# Get system health
curl -X GET "http://localhost:8000/api/health"
```

## 🔒 Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Default Limit**: 60 requests per minute per user
- **Burst Limit**: 10 requests per second
- **Headers**: Rate limit information is included in response headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
```

## 📈 Monitoring & Metrics

### Prometheus Metrics
The API exposes Prometheus metrics at `/metrics`:

```bash
curl http://localhost:8000/metrics
```

Key metrics:
- `freelancex_requests_total` - Total API requests
- `freelancex_request_duration_seconds` - Request duration
- `freelancex_agent_requests_total` - Agent-specific requests
- `freelancex_errors_total` - Total errors

### Health Check Endpoints
- `/health` - Basic health check
- `/health/detailed` - Detailed health information
- `/health/ready` - Readiness probe
- `/health/live` - Liveness probe

---

**API Reference Documentation**  
*FreelanceX.AI - Enhanced AI-Powered Freelance Assistant*  
*Version: 2.0.0 | Last Updated: 2024-01-01*
