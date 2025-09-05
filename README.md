<div align="center">

# 🎬 yt-dlp-api

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*A powerful REST API wrapper for [yt-dlp](https://github.com/yt-dlp/yt-dlp) with asynchronous job processing*

[Features](#-features) • [Quick Start](#-quick-start) • [API Documentation](#-api-documentation) • [Docker](#-docker-deployment) • [Examples](#-usage-examples)

</div>

---

## 🚀 Features

- **🔄 Asynchronous Processing**: Background job queue system for non-blocking downloads
- **🔐 Bearer Token Authentication**: Secure API access with auto-generated tokens
- **📊 Job Status Tracking**: Monitor download progress with unique job IDs
- **🐳 Docker Ready**: Complete containerization with multi-stage builds
- **⚡ Production Ready**: Gunicorn WSGI server with configurable workers
- **📁 Organized Downloads**: Automatic file organization by uploader/channel
- **🛡️ Error Handling**: Comprehensive error handling and logging
- **⏱️ Timeout Protection**: Built-in request timeouts to prevent hanging

## 📋 Requirements

- **Python**: 3.8+ (3.11+ recommended)
- **System**: FFmpeg (for video processing)
- **Dependencies**: Flask, yt-dlp, Gunicorn

## ⚡ Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/dnlrsr/yt-dlp-api.git
cd yt-dlp-api
pip install -r requirements.txt
```

### 2. Run Development Server
```bash
python index.py
```

The API will be available at `http://localhost:5000`

### 3. Get Your API Token
Check the generated `api_token.txt` file or check the server logs for your bearer token.

## 📚 API Documentation

### Authentication
All endpoints require Bearer token authentication:
```bash
Authorization: Bearer YOUR_API_TOKEN
```

### Endpoints

#### `POST /webhook`
Submit a video download job

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response (202 Accepted):**
```json
{
  "status": "pending",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "message": "Download job has been queued"
}
```

#### `GET /job/{job_id}`
Check job status and get results

**Response Examples:**

*Pending/Processing:*
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing"
}
```

*Completed:*
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "video_info": "Download details...",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

*Failed:*
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "message": "Error details..."
}
```

## 🐳 Docker Deployment

### Build & Run
```bash
# Build the image
docker build -t yt-dlp-api ./docker

# Run with volume mounting for downloads
docker run -d \
  --name yt-dlp-api \
  -p 5000:5000 \
  -v $(pwd)/youtube:/youtube \
  -v $(pwd)/api_token.txt:/app/api_token.txt \
  yt-dlp-api
```

### Docker Compose (Recommended)
```yaml
version: '3.8'
services:
  yt-dlp-api:
    build: ./docker
    ports:
      - "5000:5000"
    volumes:
      - ./youtube:/youtube
      - ./api_token.txt:/app/api_token.txt
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
```

## ⚙️ Production Deployment

### Using Gunicorn
```bash
# Install production dependencies
pip install gunicorn

# Run with custom configuration
gunicorn -c gunicorn.conf.py wsgi:app

# Or with inline config
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 300 wsgi:app
```

### Environment Variables
```bash
export PYTHONUNBUFFERED=1  # For immediate log output
export WORKERS=4           # Number of Gunicorn workers
export TIMEOUT=300         # Request timeout in seconds
```

## 💡 Usage Examples

### Python Client
```python
import requests
import time

# Your API configuration
BASE_URL = "http://localhost:5000"
API_TOKEN = "your-api-token-here"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Submit download job
response = requests.post(
    f"{BASE_URL}/webhook",
    json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
    headers=headers
)
job_data = response.json()
job_id = job_data["job_id"]

# Poll for completion
while True:
    status_response = requests.get(f"{BASE_URL}/job/{job_id}", headers=headers)
    status_data = status_response.json()
    
    if status_data["status"] in ["completed", "failed"]:
        print(f"Job {status_data['status']}")
        print(status_data)
        break
    
    print(f"Status: {status_data['status']}")
    time.sleep(5)
```

### cURL Examples
```bash
# Submit download job
curl -X POST http://localhost:5000/webhook \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Check job status
curl -X GET http://localhost:5000/job/YOUR_JOB_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📁 Project Structure

```
yt-dlp-api/
├── 📄 index.py              # Main Flask application
├── 📄 wsgi.py               # WSGI entry point
├── 📄 requirements.txt      # Python dependencies
├── 📄 gunicorn.conf.py      # Gunicorn configuration
├── 📄 api_token.txt         # Auto-generated API token
├── 🐳 docker/
│   └── 📄 Dockerfile        # Container definition
└── 📁 youtube/              # Downloaded videos (organized by uploader)
    └── 📁 Artist/
```

## 🔧 Configuration

### API Token Management
- **Auto-generated**: Token is created automatically on first run
- **Persistent**: Stored in `api_token.txt` for reuse
- **Secure**: 32-byte URL-safe random token

### Download Organization
Videos are saved to `/youtube/` with the following structure:
```
/youtube/{uploader}/{title}.{ext}
```

### Logging
- **Level**: INFO (configurable)
- **Format**: Timestamp, level, message
- **Output**: stdout with immediate flushing

## 🚨 Error Handling

The API handles various error conditions:
- **Invalid URLs**: Returns 400 with error message
- **Missing authentication**: Returns 401
- **Job not found**: Returns 404
- **Download failures**: Captured in job results
- **Timeouts**: 5-minute default timeout per job

## 🔒 Security Considerations

- **Bearer token authentication** required for all endpoints
- **Non-root user** in Docker container
- **Input validation** for all API requests
- **No direct file system access** through API

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**[dnlrsr](https://github.com/dnlrsr)**

---

<div align="center">

⭐ **Star this repository if you find it useful!** ⭐

[Report Bug](https://github.com/dnlrsr/yt-dlp-api/issues) • [Request Feature](https://github.com/dnlrsr/yt-dlp-api/issues) • [Documentation](https://github.com/dnlrsr/yt-dlp-api/wiki)

</div>
