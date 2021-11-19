#!/bin/sh

echo ${BRANCH_NAME}

echo "git setting start"

git checkout ${BRANCH_NAME}

git reset --hard HEAD
git pull origin ${BRANCH_NAME}

echo "git ${BRANCH_NAME} pull completed"

cat << EOF > /etc/init.d/celeryd
celery -A $CELERY_BIN multi start $CELERYD_NODES \
    --pidfile="$HOME/run/celery/%n.pid" \
    --logfile="$HOME/log/celery/%n%I.log" \
    --loglevel=info
EOF

cat << EOF > /etc/default/celeryd
CELERYD_NODES="worker1"
CELERY_BIN="/app/server/asyncFlask/job"
CELERY_APP="job"
CELERYD_CHDIR="/app/server/asyncFlask"
CELERYD_OPTS="--time-limit=300 --concurrency=2"
CELERYD_LOG_LEVEL="INFO".
CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
CELERYD_PID_FILE="/var/run/celery/%n.pid"
CELERYD_USER="root"
CELERYD_GROUP="root"
EOF

chmod 755 /etc/init.d/celeryd
chown root:root /etc/init.d/celeryd

cd /app/server/asyncFlask
celery multi start -A job worker --loglevel=info

cd /app
python3 /app/server/app.py

# cd /app/server/asyncFlask

# celery -A job worker --loglevel=info