FROM redis:7-alpine
COPY seed.sh /seed.sh
# sed: chuan hoa CRLF->LF phong khi clone/zip tren Windows
RUN sed -i 's/\r$//' /seed.sh && chmod +x /seed.sh
EXPOSE 6379
CMD ["sh", "/seed.sh"]
