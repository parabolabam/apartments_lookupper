FROM python:3.12-slim as python-base

# Poetry configuration
ENV POETRY_VERSION=1.7.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_VENV=/opt/poetry-venv \
    POETRY_CACHE_DIR=/opt/.cache

# Install poetry separated from system interpreter
FROM python-base as poetry-base
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Create runtime image
FROM python-base as runtime

# Copy Poetry to runtime image
COPY --from=poetry-base ${POETRY_VENV} ${POETRY_VENV}

# Add Poetry to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

# Copy project files
COPY poetry.lock pyproject.toml ./
COPY news_shepherd ./news_shepherd

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-cache --without dev

# Command to run the bot
CMD ["python", "-m", "news_shepherd.bot"]

