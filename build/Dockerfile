ARG REGISTRY=index.docker.io
FROM $REGISTRY/python:3.10.6-slim AS base



# =======================================
# STAGE builder
#
# Builds the Python virtual environment
# ======================================= 
FROM base AS builder

# proxy
ARG http_proxy
ARG https_proxy

# system env
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=1

# install poetry
RUN apt update && \
    apt install -y --no-install-recommends curl

# setup workspace
WORKDIR /usr/src/app

# install dependencies
COPY pyproject.toml .
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    /opt/poetry/bin/poetry install --no-cache --no-interaction --compile

# copy source code
COPY gistapi gistapi



# =======================================
# STAGE test
#
# Runs unit tests agains the source code
# ======================================= 
FROM builder AS test

COPY tests tests

RUN /opt/poetry/bin/poetry install --with dev && \
    /opt/poetry/bin/poetry run pytest -v



# =======================================
# STAGE production
#
# Build the production docker image with
# only required components i.e. source
# code and virtual environment
# ======================================= 
FROM base as production

# add user and group first to make sure their IDs get assigned
# consistently, regardless of whatever dependencies is added
RUN groupadd -r -g 1000 smdrm && useradd -r -d /usr/src/app -g smdrm -u 1000 smdrm

COPY --from=builder /usr/src/app /usr/src/app

WORKDIR /usr/src/app
ENV PATH="/usr/src/app/.venv/bin:$PATH"

# setup filesystem
RUN chown -R 1000:0 /usr/src/app
USER smdrm

ENTRYPOINT ["python", "gistapi/gistapi.py"]
CMD ["--help"]
