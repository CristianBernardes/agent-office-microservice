# Bloco: build do frontend (Vite) e entrega estática via nginx.
FROM node:24-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL
ARG VITE_MQTT_WS_URL
ARG VITE_DEFAULT_LANGUAGE
ARG VITE_PIX_LABEL
ARG VITE_DEFAULT_LLM_MODEL
ARG VITE_PAYPAL_URL
ARG VITE_DONATION_REMINDER_DAYS
ARG VITE_REFRESH_INTERVAL_MS
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
