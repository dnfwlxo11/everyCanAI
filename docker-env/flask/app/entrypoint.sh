#!/bin/sh

echo ${BRANCH_NAME}

echo "git setting start"

git checkout ${BRANCH_NAME}

git reset --hard HEAD
git pull origin ${BRANCH_NAME}

echo "git ${BRANCH_NAME} pull completed"

# echo "celery daemon setting start"

# nano /etc/init.d/celeryd
# nano /etc/default/celeryd

# CELERYD_NODES="flaskWorker"
# CELERY_BIN="/app/server/asyncFlask"
# CELERY_APP="classificationServer"
# CELERYD_CHDIR="/app/server"
# CELERYD_OPTS="--time-limit=300 --concurrency=2"
# CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
# CELERYD_PID_FILE="/var/run/celery/%n.pid"
# CELERYD_USER="root"
# CELERYD_GROUP="root"
# CELERY_CREATE_DIRS=1

# sudo chmod 755 /etc/init.d/celeryd
# sudo chown root:root /etc/init.d/celeryd

# /etc/init.d/celeryd start

# echo "celery daemon start"

echo $pwd
echo "server start"

python3 server/app.py

# cd /app/server/asyncFlask

# celery -A job worker --loglevel=info