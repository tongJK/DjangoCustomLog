import multiprocessing
import os


if (api_concurrency := os.getenv('API_CONCURRENCY', 1)) is None:
    api_concurrency = (multiprocessing.cpu_count() * 1.5)

api_concurrency = max(int(api_concurrency), 1)

bind = os.getenv('API_BIND', '0.0.0.0:8080')
forwarded_allow_ips = "*"

workers = api_concurrency
threads = api_concurrency

worker_class = os.getenv('WORKER_CLASS', 'uvicorn.workers.UvicornWorker')
worker_connections = int(os.getenv('WORKER_CONNECTIONS', 1000))

max_requests = os.getenv('MAX_REQUESTS', 2048)
max_requests_jitter = os.getenv('MAX_REQUEST_JITTER', 100)

timeout = int(os.getenv('TIMEOUT', 60))
graceful_timeout = int(os.getenv('GRACEFUL_TIMEOUT', 60))
keepalive = int(os.getenv('KEEP_ALIVE', 2))
reload = (reload_str := os.environ.get("API_RELOAD", "false").lower()) in ('y', 'yes', 't', 'true', 'on', '1')

errorlog = os.getenv('WORKER_CLASS', '-')  # STDOUT
accesslog = os.getenv('WORKER_CLASS', '-')  # STDOUT
loglevel = os.getenv('LOG_LEVEL', 'error')
