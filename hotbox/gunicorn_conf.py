port = 8420
workers = 1
threads = 1
timeout = 60
bind = f":{port}"
worker_class = "uvicorn.workers.UvicornWorker"
