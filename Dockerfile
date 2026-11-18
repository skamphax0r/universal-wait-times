FROM python:3.11-alpine

WORKDIR /app

# Zero external pip dependencies needed (uses Python standard library)
COPY server.py index.html ./

ENV PORT=8089 \
    PYTHONUNBUFFERED=1

EXPOSE 8089

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8089/api/health')" || exit 1

CMD ["python3", "server.py"]
