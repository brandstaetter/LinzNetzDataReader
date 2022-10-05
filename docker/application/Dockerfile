FROM python:3.9.6-slim AS poetry
ENV TZ=Etc/UTC

ENV \
  # python:
  PYTHONFAULTHANDLER=1 \
  # do not buffer stdout/stderr, gives output directly to docker log
  PYTHONUNBUFFERED=1 \
  # disable writing of .pyc files on the import of source modules
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # poetry:
  POETRY_VERSION=1.1.13 \
  POETRY_HOME="/opt/poetry" \
  PATH="$PATH:/opt/poetry/bin" \
  # virtual environment for application
  VIRTUAL_ENV=/app/venv


RUN apt-get update \
  && apt-get install --no-install-recommends -y curl \
  && rm -rf /var/lib/apt/lists/*

RUN curl -sSL 'https://install.python-poetry.org' | python -

WORKDIR /app/data_analyzer

# create and activate virtual environment
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# install production dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-root --no-ansi


##########################################
# dev stage, used for testing + building #
##########################################
FROM poetry AS dev

# install dev dependencies
RUN poetry install --no-root --no-ansi

# copy the actual application
COPY . .

# build wheel
RUN poetry build -f wheel

CMD ["/bin/bash", "-c", "mypy && pytest"]


##############################
# Application stage, default #
##############################
FROM python:3.9.6-slim AS app
ENV TZ=Etc/UTC


# Add Tini
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

# user id + group id can be passed to match permissions of volume mount
# docker build --build-arg UID=$(id -u) --build-arg GID=$(id -g) -t myapp .
ARG UID=1024
ARG GID=1024
RUN groupadd -r ourgroup -g $GID && useradd -d /app -m -r -g ourgroup -u $UID ouruser
USER ouruser

# activate virtual environment
ENV VIRTUAL_ENV=/app/venv \
  PATH="/app/venv/bin:$PATH"
# copy and install app
COPY --from=poetry --chown=ouruser:ourgroup /app/venv /app/venv
COPY --from=dev --chown=ouruser:ourgroup /app/data_analyzer/dist/*.whl dist/
RUN find dist -type f | xargs pip install --disable-pip-version-check --no-cache --no-deps

EXPOSE 8080
CMD ["uvicorn", "example_application.main:app", "--host",  "0.0.0.0", "--port", "8080", "--no-access-log"]
