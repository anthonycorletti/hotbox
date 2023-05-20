FROM python:3.11.0-slim

LABEL org.opencontainers.image.source https://github.com/anthonycorletti/hotbox

# Set workdir
WORKDIR /code

# Copy dependencies
RUN mkdir -p /code/hotbox
COPY pyproject.toml /code
COPY hotbox/__init__.py /code/hotbox

# Install dependencies
RUN apt-get update -y \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install --no-cache-dir . \
    && rm -rf $(pip cache dir)

# Copy source code
COPY . /code

# Run
ENTRYPOINT [ "gunicorn", "hotbox.api:api", "-c", "hotbox/gunicorn_conf.py" ]
