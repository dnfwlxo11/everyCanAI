#!/bin/bash

cd /app/server/asyncFlask

echo pwd
echo ls -al

celery -A job worker --loglevel=info