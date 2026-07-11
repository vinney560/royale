# gunicorn.conf.py
# ============================================
# WORKER CONFIGURATION
# ============================================

workers = 2
threads = 4
worker_class = 'gthread'
timeout = 180
keepalive = 5

# ============================================
# MEMORY MANAGEMENT
# ============================================

max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 30

# ============================================
# RESOURCE LIMITS
# ============================================

worker_max_memory = 100 * 1024 * 1024
worker_tmp_dir = '/dev/shm'

# ============================================
# NETWORK LIMITS
# ============================================

limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# ============================================
# PERFORMANCE
# ============================================

preload_app = True
worker_connections = 1000
slow_request_timeout = 30

# ============================================
# LOGGING
# ============================================

capture_output = True
accesslog = '-'
errorlog = '-'
loglevel = 'info'