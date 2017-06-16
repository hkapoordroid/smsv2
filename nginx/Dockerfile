FROM nginx:1.11.3

RUN rm /etc/nginx/nginx.conf

COPY nginx.conf /etc/nginx/

RUN rm /etc/nginx/conf.d/default.conf

COPY sms.conf /etc/nginx/conf.d/

RUN mkdir -p /usr/src/app/logs

RUN mkdir -p /usr/src/app/static

COPY ./static /usr/src/app/static