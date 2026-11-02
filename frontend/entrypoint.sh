#!/bin/sh
# Entrypoint do container de frontend: instala as dependências via
# `npm install` e gera o build de produção (vite build) a cada subida do
# container, dispensando qualquer instalação de pacotes npm no host.
# Ver frontend/Dockerfile.
set -e

cd /app

echo "[entrypoint] Instalando dependências com npm install..."
npm install

echo "[entrypoint] Gerando build de produção (vite build)..."
npm run build

echo "[entrypoint] Publicando build em /usr/share/nginx/html..."
rm -rf /usr/share/nginx/html/*
cp -r dist/. /usr/share/nginx/html/

echo "[entrypoint] Iniciando nginx..."
exec nginx -g "daemon off;"
