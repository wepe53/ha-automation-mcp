ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.13-alpine3.21
FROM ${BUILD_FROM}
RUN pip install --no-cache-dir 'mcp>=1.10,<2' 'httpx>=0.27,<1'
COPY server.py /app/server.py
COPY run.sh /run.sh
RUN chmod +x /run.sh
CMD ["/run.sh"]
