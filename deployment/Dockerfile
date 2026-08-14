# Production Multi-stage Build Dockerfile for AquaGuard Reverse Proxy & Static Frontend Service
FROM nginx:1.25-alpine

COPY deployment/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
