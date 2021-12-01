#!/bin/bash

echo ${BRANCH_NAME}

echo "git setting start"

cd /app/app_server

echo $pwd
echo $ls
echo ${cat app.js}

git checkout ${BRANCH_NAME}

git reset --hard HEAD
git pull origin ${BRANCH_NAME}

echo "git ${BRANCH_NAME} pull completed"

npm install

cat > pm2config.json << EOF
{
  "apps": [{
    "name": "app-instance",
    "script": "app.js",
    "instances": "max",
    "exec_mode": "cluster"
  }]
}
EOF

pm2-runtime start pm2config.json