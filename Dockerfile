FROM python:3.12-slim

WORKDIR /app

COPY app.py .

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080')" || exit 1

CMD ["python", "app.py"]
