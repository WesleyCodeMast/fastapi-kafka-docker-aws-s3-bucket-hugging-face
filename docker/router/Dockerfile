FROM nginx:alpine

COPY ./docker/router/etc/nginx/conf.d /etc/nginx/conf.d
COPY ./docker/router/etc/nginx/certs /etc/nginx/certs

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
