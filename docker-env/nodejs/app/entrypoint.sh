#!/bin/bash

echo ${BRANCH_NAME}

echo "git setting start"

cd /app/app_server

git checkout ${BRANCH_NAME}

git reset --hard HEAD
git pull origin ${BRANCH_NAME}

echo "git ${BRANCH_NAME} pull completed"

rm package-lock.json
rm -rf node_modules
npm install

cat > pm2config.json << EOF
{
  "apps": [{
    "name": "app-instance",
    "script": "app.js",
    "instances": "4",
    "exec_mode": "cluster"
  }]
}
EOF

pm2-runtime start pm2config.json