#!/bin/sh

echo ${BRANCH_NAME}

echo "git setting start"

git checkout ${BRANCH_NAME}

git reset --hard HEAD
git pull origin ${BRANCH_NAME}

echo "git ${BRANCH_NAME} pull completed"

chmod 755 /etc/init.d/celeryd
chown root:root /etc/init.d/celeryd

cd /app/train_server/asyncFlask
celery multi start -A job worker --loglevel=debug --logfile="./%n%I.log" --pidfile="./%n.pid" --autoscale=2,1 --max-tasks-per-child=1

cd /app
python3 /app/train_server/app.py