FROM alpine:3.19

RUN apk add --no-cache vsftpd \
    && mkdir -p /var/ftp/backup /var/run/vsftpd/empty \
    && adduser -D -H -s /sbin/nologin ftp 2>/dev/null || true

COPY vsftpd.conf /etc/vsftpd/vsftpd.conf
COPY files/ /var/ftp/

# anon_root khong duoc ghi duoc boi user ftp (vsftpd yeu cau)
RUN chown -R root:root /var/ftp && chmod -R a-w /var/ftp

EXPOSE 21 21100-21110
CMD ["vsftpd", "/etc/vsftpd/vsftpd.conf"]
