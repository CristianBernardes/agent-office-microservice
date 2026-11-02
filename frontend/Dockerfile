# Bloco: imagem única com Node (para `npm install` + build) e nginx (para
# servir os arquivos estáticos gerados). Diferente do build multi-stage
# anterior, aqui o `npm install` e o `vite build` rodam em tempo de
# execução, a cada subida do container, via entrypoint.sh — não há mais
# instalação de pacotes npm no host nem em build-time da imagem.
FROM node:24-alpine

# A imagem base node:24-alpine não inclui nginx; instalamos o pacote Alpine
# para servir os arquivos estáticos gerados pelo build.
RUN apk add --no-cache nginx

# O pacote nginx do Alpine vem com um default.conf que retorna 404 para
# tudo; substituímos por uma config que serve /usr/share/nginx/html com
# fallback de SPA.
COPY nginx.conf /etc/nginx/http.d/default.conf

WORKDIR /app
COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
