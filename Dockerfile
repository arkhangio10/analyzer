FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PORT=8080

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# Chromium is only reachable when COMPUTER_BROWSER_ENABLED is true, and it is
# false by default. It costs roughly a gigabyte of image and the cold start
# that comes with it, so a deployment that does not enable browser execution
# can leave it out with --build-arg INSTALL_BROWSER=false. The default installs
# it, so an existing build is unchanged.
ARG INSTALL_BROWSER=true
RUN if [ "$INSTALL_BROWSER" = "true" ]; then \
        playwright install --with-deps --only-shell chromium \
        && chmod -R a+rX /ms-playwright; \
    else \
        echo "Skipping Chromium; browser execution will be unavailable."; \
    fi

RUN groupadd --system --gid 10001 aprendiz \
    && useradd --system --uid 10001 --gid 10001 --no-create-home aprendiz \
    && mkdir -p /app/.runtime /data \
    && chown -R 10001:10001 /app/.runtime /data

COPY --chown=10001:10001 app ./app
# The protected evaluation set ships with the application so a mounted
# data volume cannot replace the answers a model is graded against.
COPY --chown=10001:10001 data/evaluations ./data/evaluations

USER 10001:10001

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2).read()"]

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
