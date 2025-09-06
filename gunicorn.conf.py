# Gunicorn configuration file
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
accesslog = "-"
errorlog = "-"
loglevel = "info"

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Worker {worker.pid} forked")
    
    # Ensure the worker thread is started in this worker process
    try:
        from index import ensure_worker_running
        ensure_worker_running()
        logger.info(f"Worker thread initialized for worker {worker.pid}")
    except Exception as e:
        logger.error(f"Failed to initialize worker thread for worker {worker.pid}: {e}")

def when_ready(server):
    """Called just after the server is started."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Gunicorn server is ready. Worker threads will be initialized per worker process.")
