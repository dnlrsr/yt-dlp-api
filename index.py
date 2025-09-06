import subprocess
from flask import Flask, request, jsonify
import secrets
import os
import logging
import sys
import threading
import queue
import uuid
import time

# Configure logging with immediate output to stdout
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Job queue system
job_queue = queue.Queue()
job_status = {}  # Dictionary to store job statuses
job_results = {}  # Dictionary to store job results

# Token file path
TOKEN_FILE = 'api_token.txt'

def process_download_job(job_id, video_url):
    """Process a download job in the background."""
    try:
        logger.info(f"Starting download job {job_id} for URL: {video_url}")
        job_status[job_id] = "processing"
        
        # Run yt-dlp command
        yt_dlp_command = [
            "yt-dlp", 
            video_url,
            "-o", "/youtube/%(uploader)s/%(title)s.%(ext)s"
        ]
        
        result = subprocess.run(yt_dlp_command, capture_output=True, text=True, timeout=300)
        
        logger.info(f"Job {job_id} completed with return code: {result.returncode}")
        logger.info(f"STDOUT: {result.stdout}")
        if result.stderr:
            logger.warning(f"STDERR: {result.stderr}")
        
        if result.returncode == 0:
            job_status[job_id] = "completed"
            job_results[job_id] = {
                "status": "success",
                "video_info": result.stdout.strip(),
                "url": video_url
            }
            logger.info(f"Job {job_id} completed successfully")
        else:
            job_status[job_id] = "failed"
            job_results[job_id] = {
                "status": "error",
                "message": f"yt-dlp failed: {result.stderr.strip()}"
            }
            logger.error(f"Job {job_id} failed")
            
    except subprocess.TimeoutExpired:
        job_status[job_id] = "failed"
        job_results[job_id] = {
            "status": "error",
            "message": "Request timed out"
        }
        logger.error(f"Job {job_id} timed out")
    except Exception as e:
        job_status[job_id] = "failed"
        job_results[job_id] = {
            "status": "error",
            "message": str(e)
        }
        logger.error(f"Job {job_id} failed with exception: {e}")

def worker():
    """Worker thread to process jobs from the queue."""
    while True:
        try:
            job_id, video_url = job_queue.get(timeout=1)
            process_download_job(job_id, video_url)
            job_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"Worker error: {e}")

# Start worker thread
worker_thread = threading.Thread(target=worker, daemon=True)
worker_thread.start()
logger.info("Download worker thread started")

def get_or_create_api_key():
    """Get existing API key from file or create a new one."""
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as f:
                token = f.read().strip()
            if token:  # Check if token is not empty
                log_api_key(f"Using existing API bearer key from file: {token}")
                return token
        except Exception as e:
            logger.error(f"Could not read token file: {e}")
    
    # Generate new token if file doesn't exist or is empty
    new_token = secrets.token_urlsafe(32)
    try:
        with open(TOKEN_FILE, 'w') as f:
            f.write(new_token)
        log_api_key(f"Generated new API bearer key and saved to file: {new_token}")
    except Exception as e:
        logger.error(f"Could not save token to file: {e}")
    
    return new_token

def log_api_key(message):
    """Log the API key to stdout."""
    logger.info(f"------------------------------------------")
    logger.info("")
    logger.info("IMPORTANT: Save this API bearer key securely!")
    logger.info("")
    logger.info(message)
    logger.info("")
    logger.info(f"------------------------------------------")


# Initialize API bearer key (will be set when wsgi.py imports this module)
API_BEARER_KEY = None

def init_api_key():
    """Initialize the API bearer key. Called by WSGI or development server."""
    global API_BEARER_KEY
    if API_BEARER_KEY is None:
        logger.info("Initializing API bearer key...")
        API_BEARER_KEY = get_or_create_api_key()
        logger.info("API bearer key initialization complete")
        # Force flush the logs
        import sys
        sys.stdout.flush()
        sys.stderr.flush()
    return API_BEARER_KEY

app = Flask(__name__)

# Initialize API key immediately when the app is created
init_api_key()

@app.route('/webhook', methods=['POST'])
def webhook():
    # Validate bearer token
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({
            "status": "error",
            "message": "Authorization header missing"
        }), 401
    
    if not auth_header.startswith('Bearer '):
        return jsonify({
            "status": "error",
            "message": "Invalid authorization format. Use 'Bearer <token>'"
        }), 401
    
    token = auth_header[7:]  # Remove 'Bearer ' prefix
    if token != API_BEARER_KEY:
        return jsonify({
            "status": "error",
            "message": "Invalid bearer token"
        }), 401
    
    # Process the webhook payload
    try:
        # Safely log the payload
        payload = request.get_json(silent=True)
        
        # Extract URL from payload
        if not payload or 'url' not in payload:
            return jsonify({
                "status": "error",
                "message": "Missing 'url' field in JSON payload"
            }), 400
        
        video_url = payload['url']
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Add job to queue
        job_status[job_id] = "pending"
        job_queue.put((job_id, video_url))
        
        logger.info(f"Queued download job {job_id} for URL: {video_url}")
        
        return jsonify({
            "status": "pending",
            "job_id": job_id,
            "url": video_url,
            "message": "Download job has been queued"
        }), 202
            
    except subprocess.TimeoutExpired:
        return jsonify({
            "status": "error",
            "message": "Request timed out"
        }), 408
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/job/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get the status of a download job."""
    # Validate bearer token
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({
            "status": "error",
            "message": "Authorization header missing"
        }), 401
    
    if not auth_header.startswith('Bearer '):
        return jsonify({
            "status": "error",
            "message": "Invalid authorization format. Use 'Bearer <token>'"
        }), 401
    
    token = auth_header[7:]  # Remove 'Bearer ' prefix
    if token != API_BEARER_KEY:
        return jsonify({
            "status": "error",
            "message": "Invalid bearer token"
        }), 401
    
    # Check if job exists
    if job_id not in job_status:
        return jsonify({
            "status": "error",
            "message": "Job not found"
        }), 404
    
    status = job_status[job_id]
    response = {
        "job_id": job_id,
        "status": status
    }
    
    # If job is completed or failed, include results
    if status in ["completed", "failed"] and job_id in job_results:
        response.update(job_results[job_id])
    
    return jsonify(response), 200

if __name__ == '__main__':
    # API key is already initialized when the module loads
    logger.info("Starting Flask development server...")
    logger.info("Server will run on http://0.0.0.0:5000")
    logger.warning("WARNING: This is running in development mode!")
    logger.info("For production, use: gunicorn --bind 0.0.0.0:5000 wsgi:app")
    app.run(port=5000, debug=True, host='0.0.0.0')