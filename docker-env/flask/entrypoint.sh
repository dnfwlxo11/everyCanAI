#!/bin/sh

echo ${BRANCH_NAME}

echo "git setting start"

cd /app/train_server

git checkout ${BRANCH_NAME}

git reset --hard HEAD
git pull origin ${BRANCH_NAME}

echo "git ${BRANCH_NAME} pull completed"

celery multi start -A job worker --workdir="./asyncFlask" --loglevel=debug --logfile="./%n%I.log" --pidfile="./%n.pid" --autoscale=2,1 --max-tasks-per-child=1

python3 app.py