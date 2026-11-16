#!/bin/bash
set -euxo pipefail

dnf update -y
dnf install -y docker git
systemctl enable --now docker

git clone --depth 1 --branch main \
  https://github.com/alexrbss/chatbot-algoritmos.git \
  /opt/chatbot-algoritmos

cd /opt/chatbot-algoritmos
docker build --tag chatbot-algoritmos:latest .
docker run --detach \
  --name chatbot-algoritmos \
  --restart unless-stopped \
  --publish 80:8501 \
  --env APP_READ_ONLY=true \
  chatbot-algoritmos:latest
