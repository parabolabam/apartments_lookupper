FROM python:3.12-alpine

# Set working directory
WORKDIR /app

# Install poetry
RUN pip install poetry==1.7.1

# Copy just the dependency files first
COPY pyproject.toml poetry.lock /app/

# Install dependencies
RUN poetry install --no-interaction --no-ansi

# Copy the rest of the code
COPY . /app/

# Command to run the application
CMD ["poetry", "run", "python", "-m", "news_shepherd.bot"]
