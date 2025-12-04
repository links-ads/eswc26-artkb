#!/bin/bash
echo "Starting Gunicorn."
# sleep infinity

exec gunicorn api.main:app \
    --bind 0.0.0.0:80 \
    --workers ${WORKERS} \
    --threads 2 \
    --preload \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout ${TIMEOUT} \
    --log-level "${LOG_LEVEL,,}" \
    --log-config logging.conf