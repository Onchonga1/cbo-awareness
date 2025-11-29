# Gunicorn configuration file for large file uploads
import multiprocessing

max_requests = 1000
max_requests_jitter = 100
worker_class = "sync"
workers = multiprocessing.cpu_count() * 2 + 1

# Increase timeout for large file uploads
timeout = 300

# Increase buffer sizes for large requests
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190

# Worker processes
worker_connections = 1000
keepalive = 5
