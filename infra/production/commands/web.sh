#!/bin/bash

gunicorn src.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
