FROM nginx:1.25.4-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

COPY docs/ /usr/share/nginx/html/api/docs/
