FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY services ./services
COPY tools ./tools

RUN python -m pip install --upgrade pip \
    && python -m pip install -e '.[test,dev]'

# The production application entrypoint will be supplied when Zoe Core
# orchestration is promoted to a runnable service. Keeping the image testable
# now makes CI and local integration deterministic.
CMD ["python", "-m", "pytest"]
