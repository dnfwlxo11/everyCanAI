#!/bin/sh

echo ${BRANCH_NAME}

echo "git setting start"

cd /app/train_server

git checkout ${BRANCH_NAME}

git reset --hard HEAD
git pull origin ${BRANCH_NAME}

echo "git ${BRANCH_NAME} pull completed"

cd /app/train_server/asyncFlask
# celery multi start -A job worker --loglevel=debug --logfile="./%n%I.log" --pidfile="./%n.pid" --autoscale=2,1 --max-tasks-per-child=1

python3 /app/train_server/app.py