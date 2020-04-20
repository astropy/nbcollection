#!/usr/bin/env bash

set -e
set -x
# Only runs on master
if [ -z "${CIRCLE_PULL_REQUEST}" ]; then
    git config --global user.email devnull@circleci.com
    git config --global user.name CircleCI
    mkdir -p ~/.ssh
    ssh-keyscan github.com >> ~/.ssh/known_hosts
    # Deploy gh-pages
    git clone -b build-branch --single-branch ${CIRCLE_REPOSITORY_URL} /tmp/stage-two
    rm -rf /tmp/stage-two/.circleci
    mv /tmp/stage-two-circleci /tmp/stage-two/.circleci

    cd /tmp/stage-two
    git add /tmp/stage-two/.circleci
    git commit -m "Automated deployment for Stage Two: ${BUILD_TAG}" -a
    git push origin gh-pages
    git clean -dfx
fi
exit 0
