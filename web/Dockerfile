# nginx cu (nhieu CVE cong khai) + server_tokens on -> banner/version disclosure
FROM nginx:1.18-alpine

RUN apk add --no-cache git zip

COPY html /usr/share/nginx/html
COPY default.conf /etc/nginx/conf.d/default.conf
COPY seed_git.sh /tmp/seed_git.sh

# Tao lich su .git ro ri + backup.zip luc build (sed: chuan hoa CRLF->LF phong khi clone tren Windows)
RUN sed -i 's/\r$//' /tmp/seed_git.sh && sh /tmp/seed_git.sh

EXPOSE 80
