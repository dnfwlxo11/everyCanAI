#!/bin/sh

echo ${BRANCH_NAME}

echo "git setting start"

git checkout ${BRANCH_NAME}

git reset --hard HEAD
git pull origin ${BRANCH_NAME}

echo "git ${BRANCH_NAME} pull completed"

chmod 755 /etc/init.d/celeryd
chown root:root /etc/init.d/celeryd

cd /app/server/asyncFlask
celery multi start -A job worker --loglevel=info --logfile="./%n%I.log" --pidfile="./%n.pid" --autoreload

cd /app
python3 /app/server/app.py

# cd /app/server/asyncFlask

# celery -A job worker --loglevel=info