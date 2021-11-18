#!/bin/bash

echo ${BRANCH_NAME}

git checkout ${BRANCH_NAME}

git reset --hard HEAD
git pull origin ${BRANCH_NAME}

echo "git ${BRANCH_NAME} pull completed"

echo $pwd

python3 server/app.py

cd /app/server/asyncFlask

celery -A job worker --loglevel=info