# yt-dlp-api

A simple API wrapper for [yt-dlp](https://github.com/yt-dlp/yt-dlp), allowing you to interact with yt-dlp via HTTP requests. This project is designed to run as a web service, making it easy to download and process videos from YouTube and other supported sites programmatically.

## Features
- Exposes yt-dlp functionality via a REST API
- Download videos, extract metadata, and more
- Configurable via environment variables and config files
- Docker support for easy deployment

## Requirements
- Python 3.8+
- yt-dlp
- Flask (or other supported WSGI server)
- Gunicorn (for production)

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
### Local Development
Run the API locally:
```bash
python index.py
```

### Production (Gunicorn)
```bash
gunicorn -c gunicorn.conf.py wsgi:app
```

### Docker
Build and run the Docker container:
```bash
docker build -t yt-dlp-api ./docker
# Run the container
# docker run -p 8000:8000 yt-dlp-api
```

## API Endpoints
Refer to the source code (`index.py`) for available endpoints. Typical endpoints include:
- `/download` - Download a video
- `/info` - Get video metadata

## Configuration
- `api_token.txt`: Store your API token here for authentication (if enabled)
- `gunicorn.conf.py`: Gunicorn server configuration
- `requirements.txt`: Python dependencies

## Folder Structure
- `index.py`: Main API server
- `wsgi.py`: WSGI entry point
- `docker/`: Docker-related files
- `youtube/`: Downloaded videos and data

## License
MIT

## Author
- [dnlrsr](https://github.com/dnlrsr)
