# WER Automation API - Complete Documentation

**Live API URL:** `https://wer-automation-api.fly.dev`

**Status:** ✅ Live and Active  
**Last Updated:** April 16, 2026

---

## Table of Contents
1. [Health Check](#health-check)
2. [Tool Summary Metrics](#tool-summary-metrics)
3. [WER Results](#wer-results)
4. [Performance Metrics](#performance-metrics)
5. [Tool Metrics](#tool-metrics)
6. [Example Requests](#example-requests)

---

## Health Check

### Endpoint: `GET /health`
**URL:** `https://wer-automation-api.fly.dev/health`

**Description:** Check if the API is running and healthy

**Parameters:** None

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-04-16T10:30:00Z"
}
```

**Example:**
```bash
curl https://wer-automation-api.fly.dev/health
```

---

## Tool Summary Metrics

### 1. Get Tool Summary Metrics

**Endpoint:** `GET /api/wer/get-tool-summary-metrics`

**Full URL:** `https://wer-automation-api.fly.dev/api/wer/get-tool-summary-metrics`

**Description:** Retrieve aggregated tool summary metrics (average WER per tool) for a selected language

**Parameters:**
| Parameter | Type | Required | Example | Notes |
|-----------|------|----------|---------|-------|
| `language` | string | ✅ Yes | `Hindi`, `English`, `Marathi` | Full language name for which to fetch data |

**Response Success:**
```json
{
  "status": "success",
  "data": {
    "google_translate": 0.25,
    "microsoft_translator": 0.28,
    "deepl": 0.22,
    "openai": 0.20
  }
}
```

**Response No Data:**
```json
{
  "status": "warning",
  "message": "No metrics found for hi in current or previous month",
  "data": {}
}
```

**Example Requests:**
```bash
# Get metrics for Hindi
curl "https://wer-automation-api.fly.dev/api/wer/get-tool-summary-metrics?language=Hindi"

# Get metrics for English
curl "https://wer-automation-api.fly.dev/api/wer/get-tool-summary-metrics?language=English"

# Get metrics for Marathi
curl "https://wer-automation-api.fly.dev/api/wer/get-tool-summary-metrics?language=Marathi"

# Get metrics for Punjabi
curl "https://wer-automation-api.fly.dev/api/wer/get-tool-summary-metrics?language=Punjabi"
```

---

### 2. Save Tool Summary Metrics

**Endpoint:** `POST /api/wer/save-tool-summary-metrics`

**Full URL:** `https://wer-automation-api.fly.dev/api/wer/save-tool-summary-metrics`

**Description:** Save aggregated tool summary metrics to database

**Parameters (JSON Body):**
```json
{
  "year": 2026,
  "month": "April",
  "language": "hi"
}
```

| Field | Type | Required | Example | Notes |
|-------|------|----------|---------|-------|
| `year` | integer | ✅ Yes | `2026` | Year for metrics |
| `month` | string | ✅ Yes | `April` | Month name (full name) |
| `language` | string | ✅ Yes | `Hindi` | Full language name |

**Response Success:**
```json
{
  "status": "success",
  "message": "Tool summary metrics saved"
}
```

**Response Error:**
```json
{
  "detail": "Error message here"
}
```

**Example Request:**
```bash
curl -X POST "https://wer-automation-api.fly.dev/api/wer/save-tool-summary-metrics" \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2026,
    "month": "April",
    "language": "Hindi"
  }'
```

---

## WER Results

### Endpoint: `POST /wer/save-results`

**Full URL:** `https://wer-automation-api.fly.dev/wer/save-results`

**Description:** Save Word Error Rate (WER) results for a specific tool and language

**Parameters (JSON Body):**
```json
{
  "tool": "google_translate",
  "language": "hi",
  "wer_score": 0.25,
  "timestamp": "2026-04-16T10:30:00Z",
  "audio_duration": 120,
  "accuracy": 0.75
}
```

| Field | Type | Required | Example | Notes |
|-------|------|----------|---------|-------|
| `tool` | string | ✅ Yes | `google_translate` | Name of the tool being tested |
| `language` | string | ✅ Yes | `Hindi` | Full language name |
| `wer_score` | float | ✅ Yes | `0.25` | Word Error Rate (0-1 scale) |
| `timestamp` | string | ✅ Yes | `2026-04-16T10:30:00Z` | ISO timestamp |
| `audio_duration` | integer | ❌ No | `120` | Duration in seconds |
| `accuracy` | float | ❌ No | `0.75` | Accuracy score (0-1 scale) |

**Response:**
```json
{
  "status": "success",
  "message": "WER results saved"
}
```

**Example Request:**
```bash
curl -X POST "https://wer-automation-api.fly.dev/wer/save-results" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "google_translate",
    "language": "Hindi",
    "wer_score": 0.25,
    "timestamp": "2026-04-16T10:30:00Z",
    "audio_duration": 120,
    "accuracy": 0.75
  }'
```

---

## Performance Metrics

### Endpoint: `POST /wer/save-performance`

**Full URL:** `https://wer-automation-api.fly.dev/wer/save-performance`

**Description:** Save performance metrics for tools (response time, resource usage, etc.)

**Parameters (JSON Body):**
```json
{
  "tool": "google_translate",
  "language": "hi",
  "response_time_ms": 250,
  "cpu_usage": 45.5,
  "memory_usage_mb": 256,
  "timestamp": "2026-04-16T10:30:00Z"
}
```

| Field | Type | Required | Example | Notes |
|-------|------|----------|---------|-------|
| `tool` | string | ✅ Yes | `google_translate` | Tool name |
| `language` | string | ✅ Yes | `Hindi` | Full language name |
| `response_time_ms` | float | ✅ Yes | `250` | Response time in milliseconds |
| `cpu_usage` | float | ❌ No | `45.5` | CPU usage percentage |
| `memory_usage_mb` | float | ❌ No | `256` | Memory usage in MB |
| `timestamp` | string | ✅ Yes | `2026-04-16T10:30:00Z` | ISO timestamp |

**Response:**
```json
{
  "status": "success",
  "message": "Performance metrics saved"
}
```

**Example Request:**
```bash
curl -X POST "https://wer-automation-api.fly.dev/wer/save-performance" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "google_translate",
    "language": "Hindi",
    "response_time_ms": 250,
    "cpu_usage": 45.5,
    "memory_usage_mb": 256,
    "timestamp": "2026-04-16T10:30:00Z"
  }'
```

---

## Tool Metrics

### Endpoint: `POST /wer/save-tool-metrics`

**Full URL:** `https://wer-automation-api.fly.dev/wer/save-tool-metrics`

**Description:** Save aggregated metrics for individual tools

**Parameters (JSON Body):**
```json
{
  "tool": "google_translate",
  "language": "hi",
  "avg_wer": 0.25,
  "avg_accuracy": 0.78,
  "total_tests": 150,
  "success_rate": 0.95
}
```

| Field | Type | Required | Example | Notes |
|-------|------|----------|---------|-------|
| `tool` | string | ✅ Yes | `google_translate` | Tool name |
| `language` | string | ✅ Yes | `Hindi` | Full language name |
| `avg_wer` | float | ✅ Yes | `0.25` | Average WER score |
| `avg_accuracy` | float | ❌ No | `0.78` | Average accuracy |
| `total_tests` | integer | ❌ No | `150` | Number of tests run |
| `success_rate` | float | ❌ No | `0.95` | Success rate (0-1 scale) |

**Response:**
```json
{
  "status": "success",
  "message": "Tool metrics saved"
}
```

**Example Request:**
```bash
curl -X POST "https://wer-automation-api.fly.dev/wer/save-tool-metrics" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "google_translate",
    "language": "Hindi",
    "avg_wer": 0.25,
    "avg_accuracy": 0.78,
    "total_tests": 150,
    "success_rate": 0.95
  }'
```

---

## Example Requests

### Testing with Postman

**1. Test Health Check:**
```
Method: GET
URL: https://wer-automation-api.fly.dev/health
```

**2. Get Tool Metrics:**
```
Method: GET
URL: https://wer-automation-api.fly.dev/api/wer/get-tool-summary-metrics?language=Hindi
```

**3. Save WER Results:**
```
Method: POST
URL: https://wer-automation-api.fly.dev/wer/save-results
Headers: Content-Type: application/json
Body:
{
  "tool": "google_translate",
  "language": "hi",
  "wer_score": 0.25,
  "timestamp": "2026-04-16T10:30:00Z"
}
```

---

### Testing with cURL (Command Line)

**Check if API is running:**
```bash
curl https://wer-automation-api.fly.dev/health
```

**Get Hindi metrics:**
```bash
curl "https://wer-automation-api.fly.dev/api/wer/get-tool-summary-metrics?language=Hindi"
```

**Save WER results:**
```bash
curl -X POST "https://wer-automation-api.fly.dev/wer/save-results" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "google_translate",
    "language": "Hindi",
    "wer_score": 0.25,
    "timestamp": "2026-04-16T10:30:00Z"
  }'
```

---

### Testing with Python (requests library)

```python
import requests

# Test health
response = requests.get("https://wer-automation-api.fly.dev/health")
print(response.json())

# Get metrics
response = requests.get(
    "https://wer-automation-api.fly.dev/api/wer/get-tool-summary-metrics",
    params={"language": "Hindi"}
)
print(response.json())

# Save WER results
data = {
    "tool": "google_translate",
    "language": "Hindi",
    "wer_score": 0.25,
    "timestamp": "2026-04-16T10:30:00Z"
}
response = requests.post(
    "https://wer-automation-api.fly.dev/wer/save-results",
    json=data
)
print(response.json())
```

---

### Testing with JavaScript (fetch)

```javascript
// Test health
fetch('https://wer-automation-api.fly.dev/health')
  .then(res => res.json())
  .then(data => console.log(data));

// Get metrics
fetch('https://wer-automation-api.fly.dev/api/wer/get-tool-summary-metrics?language=Hindi')
  .then(res => res.json())
  .then(data => console.log(data));

// Save WER results
const data = {
  tool: "google_translate",
  language: "Hindi",
  wer_score: 0.25,
  timestamp: "2026-04-16T10:30:00Z"
};

fetch('https://wer-automation-api.fly.dev/wer/save-results', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| `200` | ✅ Success | Data retrieved or saved successfully |
| `400` | ❌ Bad Request | Missing required parameters |
| `404` | ❌ Not Found | Endpoint doesn't exist |
| `500` | ❌ Server Error | Database or internal error |

---

## Required Headers

For `POST` requests, always include:
```
Content-Type: application/json
```

---

## Language Names

Common language names used in this API:
- `Hindi`
- `English`
- `Marathi`
- `Tamil`
- `Telugu`
- `Kannada`
- `Malayalam`
- `Gujarati`
- `Bengali`
- `Punjabi`

---

## Database Collections

Data is stored in MongoDB with these collections:
- `wer_results` - Word Error Rate results
- `performance_metrics` - Performance data
- `tool_metrics` - Tool-specific aggregated metrics
- `tool_summary_metrics` - Overall tool summaries by language

---

## Support & Troubleshooting

### Issue: 404 Not Found
**Solution:** Check the URL carefully. The routes are case-sensitive.

### Issue: 500 Server Error
**Solution:** 
- Check if MongoDB connection is active
- Verify all required parameters are provided
- Check the server logs: `flyctl logs`

### Issue: Slow Response
**Solution:** 
- May be cold start on free tier
- After first request, responses should be < 1 second

---

## API Base URL

```
https://wer-automation-api.fly.dev
```

All endpoints are relative to this base URL.

---

**Last Updated:** April 16, 2026  
**API Version:** 1.0  
**Status:** ✅ Live
