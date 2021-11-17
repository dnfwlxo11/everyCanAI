#!/bin/bash

BRANCH="master"

git checkout master

git reset --hard HEAD
git pull origin ${BRANCH}

echo "git ${BRANCH} pull completed"

python3 server/app.py