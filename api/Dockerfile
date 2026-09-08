FROM python:3.11-alpine
WORKDIR /app
RUN pip install --no-cache-dir Flask==3.0.2 gunicorn==21.2.0
COPY app.py .
EXPOSE 8000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "app:app"]
