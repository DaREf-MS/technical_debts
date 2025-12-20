FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY sites-enabled/ /etc/nginx/conf.d/

#FROM tutum/nginx
#RUN rm /etc/nginx/sites-enabled/default
#ADD sites-enabled/ /etc/nginx/sites-enabled